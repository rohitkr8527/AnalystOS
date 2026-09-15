# Frozen technology choices and decisions

| Area | Choice |
| --- | --- |
| Runtime / API / schemas | Python 3.12+, FastAPI, Pydantic |
| Agents / LLM abstraction / tools | LangGraph, LangChain, MCP |
| Model roles | Plan labels: GPT-5.6 Terra primary, Luna inexpensive, Sol evaluation judge |
| Application and warehouse DB | PostgreSQL, separate logical databases and identities |
| SQL access / validation | SQLAlchemy, SQLGlot |
| Analytics engineering / orchestration | dbt Core, Dagster |
| Jobs / queue | Celery, Redis |
| Frames / compatibility | Polars, Pandas |
| Statistics / charts | SciPy, statsmodels, Plotly |
| Frontend | Next.js, TypeScript, pnpm |
| Agent / service telemetry | LangSmith, OpenTelemetry, Prometheus, Grafana |
| Tests | Pytest, Testcontainers for PostgreSQL integration |
| Dependencies / CI / deployment | uv, GitHub Actions, Docker Compose, AWS EC2 + Nginx HTTPS |

The model names are working role labels supplied in the plan, not verified callable API IDs or pricing. API calls remain disabled. At agent implementation, validate available IDs/prices against the actual OpenAI account and store deployment IDs in non-secret config; never substitute a model silently. Dependency versions enter the lockfile as each stage installs them, rather than installing the whole future stack now.

## Decisions

1. LangGraph manages explicit state, conditional routes, persistence and bounded revisions. It is separate from Dagster, which manages data assets and quality dependencies.
2. MCP provides typed tool boundaries independent of reasoning. Every server authenticates and authorizes calls; protocol choice does not itself provide authorization.
3. dbt owns tested SQL transformations and lineage; governed metric definitions keep agents from redefining business terms.
4. One local PostgreSQL server reduces operating overhead while separate databases/users preserve application/warehouse boundaries. Warehouse migration to another engine is future work, not a claim of zero-change portability.
5. SQL proposals flow through a deterministic validator/executor under least privilege. AST checks and DB grants are independent safeguards.
6. Visualization uses registered Plotly chart specifications. It does not need an eighth autonomous agent.
7. Two critic revisions and global per-run tool/query/time/cost budgets ensure termination. Partial evidence is returned with limits instead of indefinite retries.
8. Real historical Olist data powers the demo; synthetic, versioned fixtures provide stable numeric and failure expectations.
9. Feature-oriented modules own behavior. Avoid empty classes or boilerplate service stubs before implementation.
10. Quality and metric correctness gate agents. Completing this checklist is permission to begin Stage 1; it is not evidence that agents or production controls have already been built.

Sources: [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), [dbt layered modeling](https://www.getdbt.com/blog/modular-data-modeling-techniques), [Docker Compose model](https://docs.docker.com/compose/intro/compose-application-model/).

