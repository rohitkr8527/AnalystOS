"""Offline acceptance gate for point 39. This is not the production analytics engine."""
import argparse
from collections import Counter
import csv
from decimal import Decimal
import json
from pathlib import Path
import re
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_fixtures import raw_columns
from scripts.download_olist import TABLE_FILES, inventory

CATEGORIES = {"aggregation": 20, "filtering_grouping": 20, "joins": 15,
              "trends_comparisons": 15, "metric_interpretation": 10,
              "root_cause": 10, "data_quality": 5, "statistics": 5}


def read_rows(folder, table):
    with (folder / f"{table}.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def contract_database():
    db = sqlite3.connect(":memory:")
    for table, fields in raw_columns().items():
        db.execute(f'CREATE TABLE "{table}" ({", ".join(fields)})')
        rows = read_rows(ROOT / "data/fixtures/clean", table)
        db.executemany(f'INSERT INTO "{table}" VALUES ({", ".join("?" for _ in fields)})',
                       [[row[field] for field in fields] for row in rows])
    db.executescript((ROOT / "tests/fixtures/warehouse.sql").read_text(encoding="utf-8"))
    return db


def query_rows(db, sql):
    return [[round(value, 6) if isinstance(value, float) else value for value in row]
            for row in db.execute(sql).fetchall()]


def fixture_issues(folder):
    """Small fixture integrity check, not a replacement for dbt quality tests."""
    issues = set()
    data = {}
    for table, fields in raw_columns().items():
        with (folder / f"{table}.csv").open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != fields:
                issues.add("schema_change")
            data[table] = list(reader)
    if "schema_change" in issues:
        return issues
    for table, keys in {"orders": ["order_id"], "customers": ["customer_id"],
                        "products": ["product_id"], "sellers": ["seller_id"],
                        "order_items": ["order_id", "order_item_id"],
                        "payments": ["order_id", "payment_sequential"]}.items():
        values = [tuple(row[key] for key in keys) for row in data[table]]
        if len(values) != len(set(values)):
            issues.add("duplicate_key")
        if any(not all(value) for value in values):
            issues.add("missing_key")
    for child, field, parent, parent_field in [
        ("orders", "customer_id", "customers", "customer_id"),
        ("order_items", "order_id", "orders", "order_id"),
        ("payments", "order_id", "orders", "order_id"),
        ("reviews", "order_id", "orders", "order_id"),
        ("order_items", "product_id", "products", "product_id"),
        ("order_items", "seller_id", "sellers", "seller_id"),
    ]:
        parent_keys = {row[parent_field] for row in data[parent]}
        if any(row[field] not in parent_keys for row in data[child]):
            issues.add("orphan_foreign_key")
    for row in data["orders"]:
        if not row["order_purchase_timestamp"]:
            issues.add("missing_purchase_date")
        if row["order_status"] == "delivered" and (
            not row["order_delivered_customer_date"] or not row["order_estimated_delivery_date"]
            or row["order_delivered_customer_date"] < row["order_purchase_timestamp"]
        ):
            issues.add("invalid_delivery_dates")
    if any(Decimal(row[field]) < 0 for row in data["order_items"] for field in ["price", "freight_value"]):
        issues.add("invalid_price")
    if any(not 1 <= int(row["review_score"]) <= 5 for row in data["reviews"]):
        issues.add("invalid_review_score")
    manifest = json.loads((folder / "batch.json").read_text())
    if manifest["complete_through"] < manifest["as_of"] or manifest["batch_status"] != "success":
        issues.add("stale_pipeline")
    return issues


def verify(with_raw=False):
    import yaml

    cases = json.loads((ROOT / "evaluations/cases/cases.json").read_text(encoding="utf-8"))
    golden = json.loads((ROOT / "evaluations/datasets/golden.json").read_text(encoding="utf-8"))
    assert Counter(case["category"] for case in cases) == CATEGORIES
    assert len({case["id"] for case in cases}) == len(cases) == 100
    assert len({case["question"] for case in cases}) == 100
    assert len(golden["cases"]) == len({case["case_id"] for case in golden["cases"]}) == 25
    models = yaml.safe_load((ROOT / "data_platform/dbt/model-contracts.yaml").read_text())["models"]
    metrics = yaml.safe_load((ROOT / "src/analystos/features/metrics/definitions/core.yaml").read_text())["metrics"]
    for model, spec in models.items():
        assert spec["grain"] and spec["key"] and spec["parents"], model
        assert all(parent in models or parent.startswith("raw.") and parent[4:] in raw_columns()
                   for parent in spec["parents"]), model
    for metric in metrics.values():
        assert metric["model"] in models
    by_id = {case["id"]: case for case in cases}
    with contract_database() as db:
        for case in cases:
            assert case["difficulty"] in {"easy", "medium", "hard"}
            assert case["acceptance"] and case["expected_tools"] and case["expected_result"] is not None
            assert all(table in models for table in case["expected_tables"]), case["id"]
            assert all(metric in metrics for metric in case["expected_metrics"]), case["id"]
            assert (ROOT / "data/fixtures" / case["dataset"]).is_dir()
            if case["reference_sql"]:
                assert query_rows(db, case["reference_sql"]) == case["expected_result"]["rows"], case["id"]
        for case in golden["cases"]:
            assert query_rows(db, by_id[case["case_id"]]["reference_sql"]) == case["expected_rows"], case["case_id"]
        # Independent hand-calculated anchors prevent an internally consistent wrong oracle.
        assert query_rows(db, "SELECT purchase_month, revenue, orders FROM mart_monthly_sales ORDER BY purchase_month") == [
            ["2018-01", 430.0, 7], ["2018-02", 215.0, 7], ["2018-03", 344.0, 7]]
        assert query_rows(db, "SELECT SUM(payment_value) FROM fct_payments WHERE is_valid") == [[1049.0]]
        assert query_rows(db, "SELECT COUNT(*), SUM(is_late), SUM(review_score) FROM fct_orders WHERE is_delivered") == [[18, 6, 51]]
    assert fixture_issues(ROOT / "data/fixtures/clean") == set()
    failures = json.loads((ROOT / "data/fixtures/failures.json").read_text())
    assert len(failures) == 6
    for name, expected in failures.items():
        assert fixture_issues(ROOT / "data/fixtures" / name) == {expected["expected_rule"]}, name
    for file in (ROOT / "config").glob("*.yaml"):
        assert isinstance(yaml.safe_load(file.read_text()), dict), file
    permissions = yaml.safe_load((ROOT / "config/permissions.yaml").read_text())
    groups = [set(permissions[key]) for key in ["automatic", "approval_required", "denied"]]
    assert not (groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])
    assert permissions["approval"]["agent_can_approve"] is False
    for line in (ROOT / ".env.example").read_text().splitlines():
        if line and not line.startswith("#"):
            key, value = line.split("=", 1)
            assert not value and any(word in key for word in ["PASSWORD", "SECRET", "TOKEN", "KEY"])
    for file in (ROOT / "docs").glob("*.md"):
        for link in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
            if "://" not in link and not link.startswith("#"):
                assert (file.parent / link.split("#")[0]).exists(), (file.name, link)
    if with_raw:
        manifest = json.loads((ROOT / "data/olist-manifest.json").read_text())
        assert manifest["version"] == 2
        assert set(manifest["files"]) == set(TABLE_FILES.values())
        for table, filename in TABLE_FILES.items():
            actual = inventory(ROOT / "data/raw" / filename)
            assert actual == manifest["files"][filename], filename
            assert actual["columns"] == raw_columns()[table], filename
    print("PASS: 100 cases, 25 golden answers, metric/model contracts, clean + 6 failure fixtures, policies and documentation links."
          + (" All 9 Olist CSVs verified." if with_raw else ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-raw", action="store_true")
    verify(parser.parse_args().with_raw)

