"""Atomic, typed CSV snapshot ingestion for the Olist warehouse."""

from __future__ import annotations

import csv
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Callable
from uuid import uuid4

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]
DBT_PROJECT = ROOT / "data_platform/dbt"

TABLE_FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}


def _text(value: str):
    return value or None


def _int(value: str):
    return int(value) if value else None


def _decimal(value: str):
    return Decimal(value) if value else None


def _timestamp(value: str):
    return datetime.fromisoformat(value) if value else None


Column = tuple[str, str, Callable[[str], object]]
SCHEMA: dict[str, list[Column]] = {
    "customers": [("customer_id", "text", _text), ("customer_unique_id", "text", _text),
                  ("customer_zip_code_prefix", "text", _text), ("customer_city", "text", _text),
                  ("customer_state", "text", _text)],
    "orders": [("order_id", "text", _text), ("customer_id", "text", _text),
               ("order_status", "text", _text), ("order_purchase_timestamp", "timestamp", _timestamp),
               ("order_approved_at", "timestamp", _timestamp),
               ("order_delivered_carrier_date", "timestamp", _timestamp),
               ("order_delivered_customer_date", "timestamp", _timestamp),
               ("order_estimated_delivery_date", "timestamp", _timestamp)],
    "order_items": [("order_id", "text", _text), ("order_item_id", "integer", _int),
                    ("product_id", "text", _text), ("seller_id", "text", _text),
                    ("shipping_limit_date", "timestamp", _timestamp),
                    ("price", "numeric(18,2)", _decimal),
                    ("freight_value", "numeric(18,2)", _decimal)],
    "products": [("product_id", "text", _text), ("product_category_name", "text", _text),
                 ("product_name_lenght", "integer", _int),
                 ("product_description_lenght", "integer", _int),
                 ("product_photos_qty", "integer", _int), ("product_weight_g", "integer", _int),
                 ("product_length_cm", "integer", _int), ("product_height_cm", "integer", _int),
                 ("product_width_cm", "integer", _int)],
    "sellers": [("seller_id", "text", _text), ("seller_zip_code_prefix", "text", _text),
                ("seller_city", "text", _text), ("seller_state", "text", _text)],
    "payments": [("order_id", "text", _text), ("payment_sequential", "integer", _int),
                 ("payment_type", "text", _text), ("payment_installments", "integer", _int),
                 ("payment_value", "numeric(18,2)", _decimal)],
    "reviews": [("review_id", "text", _text), ("order_id", "text", _text),
                ("review_score", "integer", _int), ("review_comment_title", "text", _text),
                ("review_comment_message", "text", _text),
                ("review_creation_date", "timestamp", _timestamp),
                ("review_answer_timestamp", "timestamp", _timestamp)],
    "geolocation": [("geolocation_zip_code_prefix", "text", _text),
                    ("geolocation_lat", "numeric(12,8)", _decimal),
                    ("geolocation_lng", "numeric(12,8)", _decimal),
                    ("geolocation_city", "text", _text), ("geolocation_state", "text", _text)],
    "product_category_translation": [("product_category_name", "text", _text),
                                     ("product_category_name_english", "text", _text)],
}


class IngestionError(RuntimeError):
    """A batch was rejected before publication."""

    def __init__(self, rule: str, detail: str):
        self.rule = rule
        super().__init__(f"{rule}: {detail}")


def warehouse_dsn(user: str = "analystos_loader", password_env: str = "WAREHOUSE_LOADER_PASSWORD") -> str:
    password = os.environ.get(password_env)
    if not password:
        raise RuntimeError(f"{password_env} is required")
    return f"host=127.0.0.1 port=5432 dbname=demo_warehouse user={user} password={password} connect_timeout=5"


def _files(folder: Path) -> dict[str, Path]:
    fixture_names = {table: f"{table}.csv" for table in SCHEMA}
    names = fixture_names if all((folder / name).exists() for name in fixture_names.values()) else TABLE_FILES
    missing = [name for name in names.values() if not (folder / name).is_file()]
    if missing:
        raise IngestionError("schema_change", f"missing files: {', '.join(missing)}")
    return {table: folder / name for table, name in names.items()}


def _manifest(folder: Path, files: dict[str, Path]) -> tuple[date, date]:
    path = folder / "batch.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("batch_status") != "success":
            raise IngestionError("stale_pipeline", "source manifest is not successful")
        as_of, complete = date.fromisoformat(data["as_of"]), date.fromisoformat(data["complete_through"])
        if complete < as_of:
            raise IngestionError("stale_pipeline", f"complete through {complete} is before requested {as_of}")
        return as_of, complete
    with files["orders"].open(encoding="utf-8", newline="") as handle:
        dates = [datetime.fromisoformat(row["order_purchase_timestamp"]).date()
                 for row in csv.DictReader(handle) if row["order_purchase_timestamp"]]
    complete = max(dates)
    return complete, complete


def _ensure_audit(conn: psycopg.Connection) -> None:
    conn.execute("CREATE SCHEMA IF NOT EXISTS ingestion")
    conn.execute("""CREATE TABLE IF NOT EXISTS ingestion.batches (
        batch_id text PRIMARY KEY, source_path text NOT NULL, started_at timestamptz NOT NULL,
        finished_at timestamptz, status text NOT NULL, as_of date, complete_through date,
        error_rule text, error_detail text)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS ingestion.files (
        batch_id text REFERENCES ingestion.batches, table_name text NOT NULL, file_name text NOT NULL,
        sha256 text NOT NULL, row_count bigint NOT NULL, PRIMARY KEY (batch_id, table_name))""")
    conn.execute("""CREATE TABLE IF NOT EXISTS ingestion.rejected_rows (
        batch_id text REFERENCES ingestion.batches, table_name text NOT NULL, line_number bigint NOT NULL,
        raw_row jsonb NOT NULL, error text NOT NULL)""")


def _record_failure(dsn: str, batch_id: str, folder: Path, error: IngestionError,
                    rejected: list[tuple[str, int, dict, str]] = ()) -> None:
    with psycopg.connect(dsn) as conn:
        _ensure_audit(conn)
        conn.execute("""INSERT INTO ingestion.batches
            (batch_id, source_path, started_at, finished_at, status, error_rule, error_detail)
            VALUES (%s, %s, %s, %s, 'failed', %s, %s)
            ON CONFLICT (batch_id) DO UPDATE SET finished_at=EXCLUDED.finished_at, status='failed',
              error_rule=EXCLUDED.error_rule, error_detail=EXCLUDED.error_detail""",
            (batch_id, str(folder), datetime.now(timezone.utc), datetime.now(timezone.utc),
             error.rule, str(error)))
        if rejected:
            with conn.cursor() as cursor:
                cursor.executemany("""INSERT INTO ingestion.rejected_rows
                    (batch_id, table_name, line_number, raw_row, error) VALUES (%s, %s, %s, %s, %s)""",
                    [(batch_id, table, line, json.dumps(row), detail)
                     for table, line, row, detail in rejected])


def _quality_checks(conn: psycopg.Connection, schema: str) -> None:
    q = lambda query: conn.execute(sql.SQL(query).format(s=sql.Identifier(schema))).fetchone()[0]
    checks = [
        ("duplicate_key", """SELECT count(*) FROM (
          SELECT 1 FROM {s}.orders GROUP BY order_id HAVING count(*) > 1 UNION ALL
          SELECT 1 FROM {s}.customers GROUP BY customer_id HAVING count(*) > 1 UNION ALL
          SELECT 1 FROM {s}.products GROUP BY product_id HAVING count(*) > 1 UNION ALL
          SELECT 1 FROM {s}.sellers GROUP BY seller_id HAVING count(*) > 1 UNION ALL
          SELECT 1 FROM {s}.order_items GROUP BY order_id, order_item_id HAVING count(*) > 1 UNION ALL
          SELECT 1 FROM {s}.payments GROUP BY order_id, payment_sequential HAVING count(*) > 1) defects"""),
        ("conflicting_review_tie", """SELECT EXISTS (SELECT 1 FROM {s}.reviews
          GROUP BY order_id, review_answer_timestamp, review_creation_date
          HAVING count(DISTINCT (review_id, review_score, review_comment_title, review_comment_message)) > 1)"""),
        ("missing_purchase_date", "SELECT EXISTS (SELECT 1 FROM {s}.orders WHERE order_purchase_timestamp IS NULL)"),
        ("orphan_foreign_key", """SELECT count(*) FROM (
          SELECT 1 FROM {s}.orders o LEFT JOIN {s}.customers c USING(customer_id) WHERE c.customer_id IS NULL UNION ALL
          SELECT 1 FROM {s}.order_items i LEFT JOIN {s}.orders o USING(order_id) WHERE o.order_id IS NULL UNION ALL
          SELECT 1 FROM {s}.order_items i LEFT JOIN {s}.products p USING(product_id) WHERE p.product_id IS NULL UNION ALL
          SELECT 1 FROM {s}.order_items i LEFT JOIN {s}.sellers x USING(seller_id) WHERE x.seller_id IS NULL UNION ALL
          SELECT 1 FROM {s}.payments p LEFT JOIN {s}.orders o USING(order_id) WHERE o.order_id IS NULL UNION ALL
          SELECT 1 FROM {s}.reviews r LEFT JOIN {s}.orders o USING(order_id) WHERE o.order_id IS NULL) defects"""),
        ("invalid_price", "SELECT EXISTS (SELECT 1 FROM {s}.order_items WHERE price < 0 OR freight_value < 0)"),
        ("invalid_status", """SELECT EXISTS (SELECT 1 FROM {s}.orders WHERE order_status IS NULL OR
          order_status NOT IN ('created','approved','invoiced','processing','shipped','delivered','canceled','unavailable'))"""),
        ("invalid_review_score", "SELECT EXISTS (SELECT 1 FROM {s}.reviews WHERE review_score NOT BETWEEN 1 AND 5)"),
        ("invalid_delivery_dates", """SELECT EXISTS (SELECT 1 FROM {s}.orders WHERE order_status='delivered' AND
          order_delivered_customer_date < order_purchase_timestamp)"""),
        ("negative_payment", """SELECT EXISTS (SELECT 1 FROM {s}.payments WHERE
          payment_value < 0 OR payment_installments < 0)"""),
    ]
    for rule, query in checks:
        if q(query):
            raise IngestionError(rule, "warehouse quality check failed")


def ingest(folder: str | Path, dsn: str | None = None) -> str:
    """Load a validated snapshot into an isolated raw schema and return its batch id."""
    folder, dsn, batch_id = Path(folder).resolve(), dsn or warehouse_dsn(), uuid4().hex
    schema = f"candidate_{batch_id}_raw"
    rejected: list[tuple[str, int, dict, str]] = []
    try:
        files = _files(folder)
        as_of, complete = _manifest(folder, files)
        with psycopg.connect(dsn) as conn:
            _ensure_audit(conn)
            conn.execute("""INSERT INTO ingestion.batches
                (batch_id, source_path, started_at, status, as_of, complete_through)
                VALUES (%s, %s, %s, 'loading', %s, %s)""",
                (batch_id, str(folder), datetime.now(timezone.utc), as_of, complete))
            conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
            for table, path in files.items():
                columns = SCHEMA[table]
                definition = sql.SQL(", ").join(
                    sql.SQL("{} {}").format(sql.Identifier(name), sql.SQL(kind)) for name, kind, _ in columns)
                conn.execute(sql.SQL("CREATE TABLE {}.{} ({})").format(
                    sql.Identifier(schema), sql.Identifier(table), definition))
                copy_sql = sql.SQL("COPY {}.{} FROM STDIN").format(
                    sql.Identifier(schema), sql.Identifier(table))
                row_count = 0
                with path.open(encoding="utf-8-sig", newline="") as handle:
                    reader = csv.DictReader(handle)
                    expected = [name for name, _, _ in columns]
                    if reader.fieldnames != expected:
                        raise IngestionError("schema_change", f"{path.name} headers do not match")
                    with conn.cursor().copy(copy_sql) as copy:
                        for line, row in enumerate(reader, 2):
                            try:
                                copy.write_row(tuple(parser(row[name]) for name, _, parser in columns))
                                row_count += 1
                            except (ValueError, TypeError, InvalidOperation) as exc:
                                rejected.append((table, line, row, str(exc)))
                if rejected:
                    raise IngestionError("parse_error", f"{len(rejected)} row(s) rejected")
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                conn.execute("""INSERT INTO ingestion.files
                    (batch_id, table_name, file_name, sha256, row_count) VALUES (%s, %s, %s, %s, %s)""",
                    (batch_id, table, path.name, digest, row_count))
            for table, columns in {
                "customers": ("customer_id",), "orders": ("order_id", "customer_id"),
                "order_items": ("order_id", "product_id", "seller_id"),
                "products": ("product_id",), "sellers": ("seller_id",),
                "payments": ("order_id",), "reviews": ("order_id",),
            }.items():
                for column in columns:
                    conn.execute(sql.SQL("CREATE INDEX ON {}.{} ({})").format(
                        sql.Identifier(schema), sql.Identifier(table), sql.Identifier(column)))
            _quality_checks(conn, schema)
            conn.execute("UPDATE ingestion.batches SET status='loaded' WHERE batch_id=%s", (batch_id,))
        return batch_id
    except IngestionError as error:
        with psycopg.connect(dsn) as cleanup:
            cleanup.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema)))
        _record_failure(dsn, batch_id, folder, error, rejected)
        raise


def build_and_publish(batch_id: str, dsn: str | None = None) -> None:
    """Build dbt in isolated schemas, then atomically swap a successful snapshot into place."""
    if not re.fullmatch(r"[0-9a-f]{32}", batch_id):
        raise ValueError("invalid batch id")
    dsn = dsn or warehouse_dsn()
    prefix = f"candidate_{batch_id}_"
    executable = shutil.which("dbt") or str(Path(sys.executable).with_name("dbt.exe"))
    command = [executable, "build", "--project-dir", str(DBT_PROJECT),
               "--profiles-dir", str(DBT_PROJECT), "--vars", json.dumps({"schema_prefix": prefix})]
    env = os.environ | {"ANALYSTOS_RAW_SCHEMA": f"{prefix}raw"}
    try:
        subprocess.run(command, check=True, env=env)
        with psycopg.connect(dsn) as conn:
            for layer in ("raw", "staging", "intermediate", "marts"):
                current, previous, candidate = layer, f"previous_{layer}", f"{prefix}{layer}"
                conn.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(previous)))
                if conn.execute("SELECT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname=%s)", (current,)).fetchone()[0]:
                    conn.execute(sql.SQL("ALTER SCHEMA {} RENAME TO {}").format(
                        sql.Identifier(current), sql.Identifier(previous)))
                conn.execute(sql.SQL("ALTER SCHEMA {} RENAME TO {}").format(
                    sql.Identifier(candidate), sql.Identifier(current)))
            conn.execute("GRANT USAGE ON SCHEMA marts TO analystos_reader")
            conn.execute("GRANT SELECT ON ALL TABLES IN SCHEMA marts TO analystos_reader")
            conn.execute("""UPDATE ingestion.batches SET status='published', finished_at=%s
                            WHERE batch_id=%s""", (datetime.now(timezone.utc), batch_id))
    except (subprocess.CalledProcessError, psycopg.Error) as exc:
        with psycopg.connect(dsn) as conn:
            for layer in ("raw", "staging", "intermediate", "marts"):
                conn.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                    sql.Identifier(f"{prefix}{layer}")))
            conn.execute("""UPDATE ingestion.batches SET status='failed', finished_at=%s,
                            error_rule='dbt_build', error_detail=%s WHERE batch_id=%s""",
                         (datetime.now(timezone.utc), str(exc), batch_id))
        raise IngestionError("dbt_build", "dbt build failed; prior snapshot retained") from exc


def run(folder: str | Path, dsn: str | None = None) -> str:
    batch_id = ingest(folder, dsn)
    build_and_publish(batch_id, dsn)
    return batch_id


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    print(run(args.folder))
