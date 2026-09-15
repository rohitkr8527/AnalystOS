# MCP and tool contracts

Three servers: warehouse, dbt and GitHub. Transport/authentication must be tested against the chosen SDK version before implementation. Do not depend on unverified specification assumptions from the draft plan.

| Server | Tools | Execution identity |
| --- | --- | --- |
| warehouse | list_schemas, list_tables, describe_table, search_columns, get_relationships, execute_query, explain_query, get_sample, get_metric | Reader for data; separate narrowly scoped metadata service |
| dbt | list_models, model_details, get_lineage, get_tests, compile_model, run_tests, run_model | Isolated dbt service; writes require bound approval |
| github | read_file, create_branch, write_file, commit, create_pull_request | Repository-scoped installation token; mutations require approval |

Permission details are in [permissions.yaml](../config/permissions.yaml). Authenticate the initiating actor at the server boundary. Tool arguments are typed, bounded and validated; file paths must stay inside the selected repository and dbt project. No arbitrary shell, module imports, database connection strings or outbound URLs from prompts.

Common request fields: run_id, actor_id, tool_call_id, tool_name, typed arguments and optional approval_id. Common response: success/error code, result/evidence reference, source version, elapsed_ms, rows/truncation, and audit ID. Never return credentials. Idempotency keys identify GitHub mutations and approved dbt runs. Replays read prior outcomes.

The warehouse execute_query path always passes through SQL validation, EXPLAIN and the controlled executor. Tool discovery does not confer execution permission. An LLM-proposed tool name cannot bypass the service allowlist.

