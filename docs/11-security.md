# Security and approval design

Authenticate API users; enforce viewer, analyst and approver roles server-side. Viewer reads authorized results/catalog; analyst starts analyses; approver approves scoped mutations. Services enforce the initiating user's scope. An agent cannot grant itself access.

Prompt text, warehouse strings and retrieved documents are untrusted data. They cannot replace system policy or supply runnable shell/Python. Mask direct identifiers from agent prompts where unnecessary; keep raw free text and geolocation inaccessible. Credentials never enter prompts, responses or committed files.

## Tool permissions and approval

[permissions.yaml](../config/permissions.yaml) freezes the allowlist. Safe bounded reads, statistics and charts run automatically. Creating/changing dbt models or metrics, expensive operations, GitHub branches/commits/PRs and dbt run_model require human approval. Destructive warehouse queries, permission changes and unrestricted secret access are denied.

Approval records bind actor, run, operation, repository/model, full proposed diff or SQL, content hash, estimated cost, expiration (24 hours) and approver. Show the exact change and checks before approval. Changed content invalidates approval. Resume uses the saved content, not newly generated content. External mutation retries require idempotency/reconciliation. Critic acceptance is not human approval. No automatic merges.

## Secrets and configuration

Non-secrets live in config/base.yaml with recursive mapping overrides from exactly one selected environment file; lists replace rather than append. Unknown/malformed settings fail validation. Secret environment values are read separately by the service that needs them; never copy them into serialized settings or telemetry.

.env.example contains secret names only. `scripts/create_local_secrets.py` creates random ignored local credentials without overwriting existing values or printing them. Optional OpenAI/LangSmith/GitHub keys are added locally only when implemented. Never fabricate account/API keys. Production secrets are supplied as restricted host-mounted files or a managed secret store through EC2 IAM, not baked into images. Rotate leaked values immediately.

PostgreSQL local init separates app owner, loader owner and marts reader. Loader/superuser credentials belong only to infrastructure, never the analytical executor. Docker local env variables are acceptable for a single-user development machine; production uses file-mounted secrets. The public API needs rate limiting, HTTPS, CSRF protections appropriate to its auth mechanism and secure cookies before deployment.

