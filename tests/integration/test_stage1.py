import csv
import json
import os
from pathlib import Path
import shutil

import psycopg
import pytest

from data_platform.ingestion import IngestionError, build_and_publish, ingest, run, warehouse_dsn

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.skipif(
    os.environ.get("ANALYSTOS_INTEGRATION") != "1", reason="set ANALYSTOS_INTEGRATION=1"
)


def _dsn(user, variable):
    return (f"host=127.0.0.1 port=5432 dbname=demo_warehouse user={user} "
            f"password={os.environ[variable]} connect_timeout=5")


@pytest.mark.integration
def test_stage1_gate(tmp_path):
    clean = ROOT / "data/fixtures/clean"
    batch_id = run(clean)
    with psycopg.connect(warehouse_dsn()) as conn:
        assert conn.execute("select sum(item_price) from marts.fct_order_items where is_valid").fetchone()[0] == 989
        assert conn.execute("select sum(revenue) from marts.fct_orders where is_valid").fetchone()[0] == 989
        assert conn.execute("select sum(revenue) from marts.mart_monthly_sales").fetchone()[0] == 989
        assert conn.execute("select count(*) from ingestion.files where batch_id=%s", (batch_id,)).fetchone()[0] == 9

    failures = json.loads((ROOT / "data/fixtures/failures.json").read_text())
    for name, expected in failures.items():
        with pytest.raises(IngestionError) as rejected:
            ingest(ROOT / "data/fixtures" / name)
        assert rejected.value.rule == expected["expected_rule"]

    bad = tmp_path / "bad_parse"
    shutil.copytree(clean, bad)
    path = bad / "order_items.csv"
    rows = list(csv.reader(path.open(encoding="utf-8", newline="")))
    rows[1][5] = "not-a-number"
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerows(rows)
    with pytest.raises(IngestionError, match="parse_error"):
        ingest(bad)
    with psycopg.connect(warehouse_dsn()) as conn:
        assert conn.execute("select count(*) from ingestion.rejected_rows").fetchone()[0] >= 1

    candidate = ingest(clean)
    with psycopg.connect(warehouse_dsn()) as conn:
        conn.execute(f'update "candidate_{candidate}_raw".order_items set price=-1 where order_id=\'o101\'')
    with pytest.raises(IngestionError, match="dbt_build"):
        build_and_publish(candidate)
    with psycopg.connect(warehouse_dsn()) as conn:
        assert conn.execute("select sum(revenue) from marts.mart_monthly_sales").fetchone()[0] == 989

    with psycopg.connect(_dsn("analystos_reader", "WAREHOUSE_PASSWORD")) as reader:
        assert reader.execute("select current_user").fetchone()[0] == "analystos_reader"
        with pytest.raises((psycopg.errors.ReadOnlySqlTransaction, psycopg.errors.InsufficientPrivilege)):
            reader.execute("delete from marts.fct_orders")
    with pytest.raises(psycopg.OperationalError):
        psycopg.connect(_dsn("analystos_app", "APP_DATABASE_PASSWORD"))
