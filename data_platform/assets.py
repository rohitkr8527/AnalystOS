"""Dagster assets for the Stage 1 warehouse pipeline."""

from pathlib import Path
import os

from dagster import AssetExecutionContext, Definitions, asset

from data_platform.ingestion import build_and_publish, ingest


@asset
def raw_snapshot(context: AssetExecutionContext) -> str:
    folder = Path(os.environ.get("ANALYSTOS_DATASET", "data/raw"))
    batch_id = ingest(folder)
    context.add_output_metadata({"batch_id": batch_id, "source": str(folder)})
    return batch_id


@asset
def warehouse_snapshot(raw_snapshot: str) -> None:
    build_and_publish(raw_snapshot)


defs = Definitions(assets=[raw_snapshot, warehouse_snapshot])
