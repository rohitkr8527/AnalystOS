# Testing strategy

Current runnable gate: `uv run pytest -q` or `uv run python scripts/verify_foundation.py`. Checks cover contract references, case/category counts, frozen golden outputs, fixture relationships and anomaly expectations, and secret/config separation. `--with-raw` also checks all source file hashes, row counts and headers.

## Fixture contract

`data/fixtures/clean` is synthetic source-shaped CSV data, independent of Olist. Version 1 has three complete months, recurring people with distinct order customer IDs, multiple items and split payment components, canceled orders, multiple categories/states/sellers, nullable undelivered dates and late deliveries. Fixed IDs and dates make results deterministic. It contains no real customer information.

`scripts/build_fixtures.py` reproduces CSVs and materializes six broken fixture directories. `data/fixtures/failures.json` defines the exact expected defect, rule and response. They include duplicates, missing dates, orphan foreign keys, invalid prices, schema change and stale pipeline. Failure datasets are full snapshots so no hidden overlay loader is required. A successful old archive is not considered a failed live pipeline: compare its logical watermark to the fixture's as_of.

The tiny SQLite contract harness is test-only. It independently models the frozen fact grain and tests reference SQL. It is not a replacement warehouse or a production query executor. Golden expected rows are static, not recalculated during tests.

## Later gates by stage

- Stage 1: Pytest/Testcontainers PostgreSQL with fixture loads, raw parse failures, dbt keys/FKs/ranges/fanout/reconciliation, Dagster failed publication.
- Stage 2: SQL AST negative and positive tests, read-only privilege tests, EXPLAIN timeout/cost and row caps, metrics/statistics/chart schemas.
- Stage 3: MCP argument/result schemas, auth scope, missing server, retry/idempotency and permission contract tests.
- Stages 4–5: isolated agents with fixed tool evidence, workflow routing/quality stop, budgets, malformed model output, bounded revisions and checkpoint resume.
- Stages 6–7: authenticated API/browser login → question → result → inspect SQL/evidence/chart; approval denial/expiry and role isolation.
- Stage 9: DB/Redis outage, slow queries, schema drift, dbt failure, missing data, provider timeouts; no silent result loss or duplicate external mutations.
- Stage 10: 100-case benchmark and frozen 25-case regression suite, cost and latency report.

CI currently runs the offline foundation gate. Real integration and browser checks become required when their implementation lands. No tests make paid LLM calls by default.
