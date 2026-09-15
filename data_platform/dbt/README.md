# dbt design skeleton

Model SQL will be implemented in Stage 1. `model-contracts.yaml` is a design artifact, not an enforced dbt model contract. Sources are source-shaped raw tables in `../raw_schema.sql`.

The schema macro intentionally maps the configured layer names directly to `staging`, `intermediate` and `marts` in the dedicated local warehouse. Each developer/CI job must use a separate database; do not share this profile across developers in one database. Production uses the same fixed layer names with the loader role.

Copy `profiles.example.yml` outside version control or pass its directory as dbt profiles location after creating an actual profiles.yml. Export WAREHOUSE_LOADER_PASSWORD into the dbt process environment; dbt does not automatically load the root .env. Never put a password in a checked-in profile.

