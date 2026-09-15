# Local development

Prerequisites: Git, Python 3.12+, uv, Docker Desktop with the Linux engine. Node.js and pnpm are needed at the frontend stage. No OpenAI, LangSmith, GitHub token or AWS account is needed for this milestone.

```powershell
uv sync --locked
uv run pytest -q
python scripts/download_olist.py
uv run python scripts/verify_foundation.py --with-raw
python scripts/create_local_secrets.py
docker compose config --quiet
docker compose up -d --wait
docker compose ps
```

The initial Compose stack has PostgreSQL 17 (analystos_app and demo_warehouse on one server) and Redis 7.4. Ports bind only to 127.0.0.1. App, reader and loader credentials are separate. Init scripts run only on a new PostgreSQL volume; editing .env does not rotate an existing database password. Rotate via PostgreSQL administration, not by deleting a volume containing data.

Shell scripts are checked in with LF endings. PostgreSQL's entrypoint sources the initialization script. Stop containers with `docker compose stop`; `docker compose down` preserves the named DB volume. Deleting volumes is destructive and not a normal bootstrap step.

Use local.yaml for host processes and base.yaml for Compose services. The future config loader merges mappings recursively, replaces lists and rejects unknown keys. The current configuration files define that contract; no runtime configuration service is claimed.

Later stages add API, worker, MCP, Dagster, web and telemetry services as implemented. `make demo-setup` and `make dev` from the long-term plan will be added when those flows actually work. This milestone does not claim to run an agent or populate the warehouse.
