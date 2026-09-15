"""Fetch the pinned public Olist archive; verify and extract expected CSVs only."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
URL = "https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce?datasetVersionNumber=2"
TABLE_FILES = {
    name: f"olist_{source}_dataset.csv" for name, source in {
        "customers": "customers", "orders": "orders", "order_items": "order_items",
        "products": "products", "sellers": "sellers", "payments": "order_payments",
        "reviews": "order_reviews", "geolocation": "geolocation",
    }.items()
}
TABLE_FILES["product_category_translation"] = "product_category_name_translation.csv"


def inventory(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        columns = next(reader)
        rows = 0
        for row in reader:
            if len(row) != len(columns):
                raise ValueError(f"Invalid CSV row in {path.name}")
            rows += 1
    if not rows:
        raise ValueError(f"Empty dataset file: {path.name}")
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    return {"sha256": digest, "rows": rows, "columns": columns, "bytes": path.stat().st_size}


def main():
    target = ROOT / "data/raw"
    target.mkdir(parents=True, exist_ok=True)
    if any((target / name).exists() for name in TABLE_FILES.values()):
        raise SystemExit("Raw files already exist; run uv run python scripts/verify_foundation.py --with-raw.")
    downloads = ROOT / "data/downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    archive = downloads / "olist-v2.zip"
    if not archive.exists():
        partial = archive.with_suffix(".part")
        request = urllib.request.Request(URL, headers={"User-Agent": "AnalystOS-data-bootstrap/0.1"})
        with urllib.request.urlopen(request, timeout=120) as response, partial.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        if not zipfile.is_zipfile(partial):
            raise SystemExit("Kaggle did not return a ZIP. See data/README.md for authenticated download.")
        partial.replace(archive)
    with zipfile.ZipFile(archive) as bundle:
        for filename in TABLE_FILES.values():
            entry = bundle.getinfo(filename)
            if entry.file_size > 500_000_000:
                raise ValueError(f"Unexpectedly large file: {filename}")
        for filename in TABLE_FILES.values():
            with bundle.open(filename) as source, (target / filename).open("xb") as output:
                shutil.copyfileobj(source, output)
    manifest = {
        "dataset": "olistbr/brazilian-ecommerce", "version": 2, "source_url": URL,
        "obtained_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": {name: inventory(target / name) for name in TABLE_FILES.values()},
    }
    (ROOT / "data/olist-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Obtained and inventoried {len(manifest['files'])} Olist CSVs; raw files remain gitignored.")


if __name__ == "__main__":
    main()
