# AnalystOS

An autonomous data engineering and analytics team for the Olist e-commerce warehouse.

**Current milestone: Stage 1 complete.** The repository includes validated CSV ingestion, PostgreSQL/dbt warehouse models and Dagster assets. Agent services and the web application are later stages.

Start with the [completed checklist](docs/00-predevelopment-checklist.md), [scope](docs/01-product-overview.md), and [local development guide](docs/13-local-development.md).

Follow the [implementation stages](docs/17-implementation-stages.md) for the remaining work, dependencies and completion gates.

## Verify the foundation

```powershell
uv sync --locked
uv run pytest -q
uv run python scripts/verify_foundation.py --with-raw
```

Tests use committed synthetic CSVs; no API keys, database, Docker or network are needed. The optional `--with-raw` check also verifies your locally downloaded Olist files against the acquisition manifest.

## Get the demo data

```powershell
python scripts/download_olist.py
```

The real dataset stays in ignored `data/raw/`. See [source, license and limitations](data/README.md). Synthetic fixtures are separate and versioned.

## Start local infrastructure

```powershell
python scripts/create_local_secrets.py
docker compose up -d --wait
```

This starts one PostgreSQL server containing separate application and warehouse databases, plus Redis. Docker Desktop must be running. No cloud resources or paid model calls are made.

## Build the warehouse

```powershell
uv run python -m data_platform.ingestion data/fixtures/clean
uv run python -m data_platform.ingestion data/raw
```

Each run builds in isolated schemas and atomically publishes only after dbt succeeds. Set `ANALYSTOS_DATASET` and run `uv run dagster dev -m data_platform.assets` to use the two Dagster assets.

## Repository map

| Path | Responsibility |
| --- | --- |
| `apps/` | Future API, worker and Next.js entry points |
| `src/analystos/features/` | Feature modules for analytics and engineering |
| `src/analystos/platform/` | Shared infrastructure boundaries |
| `mcp_servers/` | Warehouse, dbt and GitHub tool boundaries |
| `data_platform/` | Raw schema, dbt layer contracts and Dagster assets |
| `data/` | Acquisition documentation and synthetic fixtures |
| `evaluations/` | 100 planned cases, 25 frozen golden cases |
| `config/` | Non-secret YAML configuration and policy contracts |
| `infra/`, `observability/` | Deployment and telemetry locations |
| `docs/` | Design, scope, security and acceptance criteria |

The project technology choices are frozen in [design decisions](docs/16-design-decisions.md). Libraries are installed when their implementation stage begins; this milestone only needs the test tools.
