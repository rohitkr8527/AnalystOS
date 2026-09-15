# Point 39 — pre-development checklist

Baseline completed on 2026-09-16. These checks establish the agreed design and test data before implementing agents. Runtime services and enforcement are explicitly assigned to later stages.

| Done | Requirement | Concrete artifact |
| --- | --- | --- |
| [x] | Final project scope frozen | [Product scope](01-product-overview.md) |
| [x] | Tech stack frozen | [Technology choices and decisions](16-design-decisions.md), [test dependency lock](../uv.lock) |
| [x] | Olist dataset obtained | Nine local ignored CSVs; [acquisition manifest with hashes](../data/olist-manifest.json) |
| [x] | Dataset documented | [Source, acquisition, attribution and limits](../data/README.md) |
| [x] | Raw-table schema designed | [Nine-table PostgreSQL DDL](../data_platform/raw_schema.sql), [grains and ingestion](04-data-architecture.md) |
| [x] | Warehouse dimensional model designed | [Warehouse design](05-warehouse-design.md), [31 model contracts](../data_platform/dbt/model-contracts.yaml) |
| [x] | dbt layers designed | [dbt project](../data_platform/dbt/dbt_project.yml), sources, layer directories and schema naming |
| [x] | Core metrics defined | [Nine versioned metrics](../src/analystos/features/metrics/definitions/core.yaml), [semantics](06-metric-layer.md) |
| [x] | Data-quality rules defined | [Fourteen rules, severities and actions](../config/data-quality.yaml) |
| [x] | Four demo scenarios defined | [Basic BI, investigation, incident and dbt engineering](15-demo-scenarios.md) |
| [x] | Approximately 100 evaluation questions planned | [100 questions](../evaluations/README.md), [structured cases and expected results](../evaluations/cases/cases.json) |
| [x] | Golden test set defined | [25 static numeric expectations](../evaluations/datasets/golden.json) |
| [x] | Test fixture dataset defined | [147 synthetic source rows](../data/fixtures/clean), [reproducible generator](../scripts/build_fixtures.py) |
| [x] | Failure fixtures defined | [Six full failure snapshots and expected rules](../data/fixtures/failures.json) |
| [x] | Seven agent responsibilities frozen | [Inputs, outputs, tools and routing](03-agent-architecture.md) |
| [x] | Tool permissions defined | [Permission matrix](../config/permissions.yaml), [MCP boundaries](07-mcp-architecture.md) |
| [x] | Human approval rules defined | [Approval binding, expiry, invalidation and replay rules](11-security.md) |
| [x] | SQL security policy defined | [AST, catalog, function, cost, timeout and row policies](08-sql-security.md) |
| [x] | Agent execution budgets defined | [Time, calls, queries, revisions, concurrency and USD limits](../config/base.yaml) |
| [x] | Repository structure created | [Repository map](../README.md); feature folders, apps, infrastructure and tests; local Git initialized |
| [x] | Configuration strategy created | [Base config](../config/base.yaml), local/test/production overrides; [merge contract](13-local-development.md) |
| [x] | Secret handling created | [Secret names only](../.env.example), ignored random local .env, [non-overwriting creation script](../scripts/create_local_secrets.py) |
| [x] | Docker development architecture defined | [Compose PostgreSQL + Redis](../docker-compose.yml), [separate databases and roles](../infra/docker/init-databases.sh) |
| [x] | AWS deployment architecture defined | [EC2, HTTPS, network access, backups and release design](14-aws-deployment.md) |
| [x] | Documentation structure created | Sixteen design documents plus this checklist and domain READMEs |

## Verification

```powershell
uv sync --locked
uv run pytest -q
uv run python scripts/verify_foundation.py --with-raw
docker compose config --quiet
```

The offline gate verifies all numeric reference results, 25 golden answers, independent hand-calculated anchors, source and failure fixture integrity, model/metric references, policy separation, empty secret examples and documentation links. The raw option additionally validates all nine acquired CSV hashes, row counts and headers against their schema. Real source data remains excluded from Git.

Compose configuration is validated. Docker Desktop's Linux daemon was stopped during this task, so database initialization/container health have **not** been runtime-tested. This does not prevent the requested architecture design from being complete. Start Docker Desktop and run `docker compose up -d --wait` during Stage 1.

No agents, production SQL executor, dbt model builds, AWS resources, external GitHub repository or paid model calls were created. Those implementations are beyond this pre-development checklist. Model API IDs and pricing remain deployment-time checks; the plan's model role labels are preserved with calls disabled.

The next implementation milestone is now Stage 2; Stage 1 delivered validated ingestion, dbt staging/intermediate/marts, warehouse tests and Dagster assets.
