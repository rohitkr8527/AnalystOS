"""Reproduce synthetic source-shaped fixture v1; never changes golden expectations."""
import csv
from datetime import datetime, timedelta
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "data/fixtures"


def raw_columns():
    ddl = (ROOT / "data_platform/raw_schema.sql").read_text(encoding="utf-8")
    return {
        table: re.findall(r"(?:^|,)\s*(\w+)\s+(?:text|integer|timestamp|numeric)", body)
        for table, body in re.findall(r"CREATE TABLE raw\.(\w+)\s*\((.*?)\);", ddl, re.S)
    }


def write_csv(path, columns, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def build():
    clean = FIXTURES / "clean"
    clean.mkdir(parents=True, exist_ok=True)
    columns = raw_columns()
    rows = {table: [] for table in columns}
    states = ["SP", "RJ", "MG"]
    categories = ["eletronicos", "livros", "casa"]
    for i in range(1, 7):
        rows["products"].append(dict(zip(columns["products"],
            [f"p{i}", categories[(i-1) % 3], 10, 30, 1, 500, 20, 10, 15])))
    for i, state in enumerate(states, 1):
        rows["sellers"].append(dict(zip(columns["sellers"], [f"s{i}", f"0{i}000", f"city{i}", state])))
        for offset in [0, 0.01]:
            rows["geolocation"].append(dict(zip(columns["geolocation"],
                [f"0{i}000", -20-i+offset, -40-i, f"city{i}", state])))
    for category, english in zip(categories, ["electronics", "books", "home"]):
        rows["product_category_translation"].append(dict(zip(columns["product_category_translation"], [category, english])))
    for month, factor in [(1, 10), (2, 5), (3, 8)]:
        for n in range(1, 9):
            order = f"o{month}{n:02}"
            customer = f"c{month}{n:02}"
            location = (n-1) % 3
            purchase = datetime(2018, month, n*3)
            estimated = purchase + timedelta(days=4)
            delivered = purchase + timedelta(days=6 if n % 3 == 0 else 3)
            status = "canceled" if n == 8 else "shipped" if n == 7 else "delivered"
            rows["customers"].append(dict(zip(columns["customers"],
                [customer, f"u{n}", f"0{location+1}000", f"city{location+1}", states[location]])))
            rows["orders"].append(dict(zip(columns["orders"], [order, customer, status,
                purchase, purchase + timedelta(hours=1), purchase + timedelta(days=1),
                delivered if status == "delivered" else "", estimated])))
            total = 0
            for item in range(1, 3 if n % 2 == 0 else 2):
                price = factor * (n + item - 1)
                total += price + 2
                rows["order_items"].append(dict(zip(columns["order_items"],
                    [order, item, f"p{(n+item-2)%6+1}", f"s{location+1}",
                     purchase+timedelta(days=2), price, 2])))
            for seq in range(1, 3 if n == 2 else 2):
                rows["payments"].append(dict(zip(columns["payments"],
                    [order, seq, "voucher" if seq == 2 else "credit_card", 1,
                     total/2 if n == 2 else total])))
            if status == "delivered":
                rows["reviews"].append(dict(zip(columns["reviews"],
                    [f"r{month}{n}", order, n%5+1, "", "", delivered, delivered+timedelta(days=1)])))
    for table, values in rows.items():
        write_csv(clean / f"{table}.csv", columns[table], values)
    manifest = {"version": 1, "synthetic": True, "as_of": "2018-03-31",
                "complete_through": "2018-03-31", "batch_status": "success"}
    (clean / "batch.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    failures = {
        "duplicates": ("orders", "duplicate_key"),
        "missing_dates": ("orders", "missing_purchase_date"),
        "orphan_foreign_keys": ("order_items", "orphan_foreign_key"),
        "invalid_prices": ("order_items", "invalid_price"),
        "schema_change": ("orders", "schema_change"),
        "stale_pipeline": ("orders", "stale_pipeline"),
    }
    for name, (table, rule) in failures.items():
        target = FIXTURES / name
        shutil.copytree(clean, target, dirs_exist_ok=True)
        altered = [dict(row) for row in rows[table]]
        fields = list(columns[table])
        if name == "duplicates":
            altered.append(dict(altered[0]))
        elif name == "missing_dates":
            altered[0]["order_purchase_timestamp"] = ""
        elif name == "orphan_foreign_keys":
            altered[0]["order_id"] = "missing_order"
        elif name == "invalid_prices":
            altered[0]["price"] = -1
        elif name == "schema_change":
            fields.remove("order_purchase_timestamp")
            for row in altered:
                del row["order_purchase_timestamp"]
        elif name == "stale_pipeline":
            removed = {row["order_id"] for row in altered
                       if row["order_purchase_timestamp"] > datetime(2018, 3, 15, 23, 59, 59)}
            altered = [row for row in altered if row["order_id"] not in removed]
            for child in ["order_items", "payments", "reviews"]:
                write_csv(target / f"{child}.csv", columns[child],
                          [row for row in rows[child] if row["order_id"] not in removed])
            (target / "batch.json").write_text(json.dumps(
                {**manifest, "complete_through": "2018-03-15", "batch_status": "incomplete"}, indent=2)+"\n", encoding="utf-8")
        write_csv(target / f"{table}.csv", fields, altered)
    (FIXTURES / "failures.json").write_text(json.dumps({name: {
        "expected_rule": rule, "affected_table": table, "expected_severity": "error",
        "expected_response": "Identify the defect, show evidence and block unsupported business conclusions."
    } for name, (table, rule) in failures.items()}, indent=2)+"\n", encoding="utf-8")
    print(f"Built fixture v1: {sum(map(len, rows.values()))} clean source rows and six failure snapshots.")


if __name__ == "__main__":
    build()

