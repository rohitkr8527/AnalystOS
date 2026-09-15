# Implementation stages

## Baseline and scope

As of 2026-09-16, the [pre-development foundation](00-predevelopment-checklist.md) and Stage 1 warehouse pipeline are complete. PostgreSQL and Redis are running locally; typed ingestion, all 31 dbt models, warehouse quality tests and Dagster assets are implemented. Deterministic analytics, tools, agents and application services remain to be implemented, beginning with Stage 2.

This roadmap covers the [frozen V1 scope](01-product-overview.md) and preserves the stage numbers already used in the [testing strategy](12-testing-strategy.md). Complete each stage's acceptance gate before dependent work. Install and lock dependencies when their stage begins. Add security checks, tests and telemetry alongside the behavior they protect.

## Stage summary

| Stage | Deliverable | Depends on | Status |
| --- | --- | --- | --- |
| 0 | Scope, contracts, fixtures and foundation checks | None | Complete |
| 1 | Validated warehouse and data pipeline | 0 | Complete |
| 2 | Deterministic analytics and safe SQL execution | 1 | Next |
| 3 | Authenticated MCP tool servers | 2 | Planned |
| 4 | Seven individually tested agents | 3 | Planned |
| 5 | Persistent, bounded analysis workflow | 4 | Planned |
| 6 | Authenticated API, jobs and approval lifecycle | 5 | Planned |
| 7 | Usable analysis workspace | 6 | Planned |
| 8 | Approved dbt engineering and GitHub PR workflow | 7 | Planned |
| 9 | Operational hardening and recovery | 8 | Planned |
| 10 | Evaluation results and release gate | 9 | Planned |
| 11 | Deployment and reproducible demo handoff | 10 | Planned |

## Stage 0 — Pre-development foundation

**Delivered:** frozen scope and stack, source acquisition/schema, warehouse and metric contracts, quality/security policies, synthetic clean and failure fixtures, 100 evaluation cases, 25 golden cases, local infrastructure design and offline CI.

**Gate:** retained. The foundation checks still pass, and Stage 1 runtime-verified Docker service health, database initialization and role separation.

## Stage 1 — Warehouse and data pipeline

**Goal:** produce trustworthy marts before any agent consumes data.

**Status:** Complete (2026-09-16).

- [x] Start PostgreSQL and Redis; verify separate application, loader and reader identities.
- [x] Implement typed ingestion for all nine source CSVs, with header validation, rejected-row provenance, hashes and batch completeness metadata.
- [x] Implement the 31 dbt model contracts in dependency order: staging, intermediate, dimensions/facts and analytical marts.
- [x] Enforce grain, deduplication, key, relationship, range and revenue reconciliation rules; preserve the defined metric semantics.
- [x] Add Dagster assets for ingestion and dbt builds. Publish only successful snapshots and preserve the previous good marts after failure.
- [x] Validate synthetic clean/failure datasets in PostgreSQL, then load the acquired Olist dataset.

**Gate passed:** PostgreSQL integration and dbt tests pass; all six failure fixtures produce the expected failure behavior; failed loads/builds do not replace good data; valid item, order and monthly revenue reconcile. Dataset hashes and measured Olist reference results are captured.

**Evidence:** the integration gate covers clean ingestion, all six failure fixtures, parse provenance, failed-build rollback, role isolation and the 989.00 BRL synthetic reconciliation anchor. The final suite passed 2 tests; the Olist dbt gate passed 35 tests with one expected data warning and no errors. The acquired Olist build reconciles 13,494,400.74 BRL across item, order and monthly grains; hashes remain pinned in the acquisition manifest and are recorded per batch. Eight source orders labeled delivered lack delivery timestamps, so they are retained, warned and excluded from delivery-eligible metrics. Measured anchors are in [olist-reference-results.json](../data/olist-reference-results.json).

**References:** [ingestion](04-data-architecture.md), [warehouse](05-warehouse-design.md), [local setup](13-local-development.md).

## Stage 2 — Deterministic analytics and SQL safety

**Goal:** make every analytical operation safe and testable without an LLM.

**Status:** Next.

- [ ] Implement validated configuration loading, vetted catalog/lineage lookup and versioned metric resolution.
- [ ] Build the shared SQL validator and executor: full AST checks, catalog/function allowlists, parameter binding, EXPLAIN cost checks, read-only grants, timeout and bounded results.
- [ ] Expose quality results and logical batch freshness through deterministic services.
- [ ] Implement registered statistical operations, Plotly chart specifications and evidence/report schemas.
- [ ] Persist query provenance, metric/model versions, truncation and calculation limitations; exclude restricted raw fields.

**Done when:** valid aggregates, windows and CTEs execute; the SQL policy's negative cases fail closed; database grants independently reject writes; timeout and result caps work. Metric edge cases and statistics/chart schemas have runnable checks against fixed inputs.

**References:** [metrics](06-metric-layer.md), [SQL policy](08-sql-security.md), [evidence requirements](10-observability.md).

## Stage 3 — MCP tool boundaries

**Goal:** expose the tested services through three authorized tool servers.

- [ ] Implement warehouse, dbt and GitHub MCP request/response contracts with the selected SDK and transport.
- [ ] Authenticate service calls and enforce the initiating actor's scope, typed arguments, path restrictions and tool allowlists.
- [ ] Route every warehouse query through the Stage 2 executor.
- [ ] Support dbt inspection and isolated compilation/tests; define mutation handlers with approval verification and idempotency.
- [ ] Reject mutations without valid bound approvals; keep live mutation use gated until the approval workflow is available.

**Done when:** contract tests cover schemas, authorization, forbidden tools/paths, unavailable servers and retry behavior. Discovery or delegation cannot broaden access; replay cannot duplicate a mutation.

**References:** [MCP architecture](07-mcp-architecture.md), [permissions](../config/permissions.yaml).

## Stage 4 — Individual agents

**Goal:** implement the seven frozen responsibilities against controlled tools.

- [ ] Configure the LLM adapter and validate actual account model IDs and pricing before enabling paid calls; retain explicit deployment configuration.
- [ ] Implement Metadata, Data Quality, SQL Analyst, Statistical Analyst, Business Analyst, Critic and Analytics Manager agents with typed inputs/outputs.
- [ ] Keep SQL execution, statistics and chart rendering in deterministic services.
- [ ] Test each responsibility with fixed evidence and controlled model responses, including malformed output and untrusted source text.

**Done when:** agents select permitted tools and metrics, handle insufficient evidence, and emit schema-valid results. SQL Analyst only proposes SQL; interpretation cannot introduce unsupported numbers or causal claims. Default tests make no paid calls.

**Reference:** [agent contracts](03-agent-architecture.md).

## Stage 5 — End-to-end analysis workflow

**Goal:** orchestrate the agents into a recoverable LangGraph run.

- [ ] Implement intent resolution, metadata/metrics, quality gate, SQL, optional statistics, interpretation, critic and report routing.
- [ ] Persist run state/checkpoints and evidence references; keep large results outside prompts/checkpoints.
- [ ] Enforce shared time, tool, query, cost and concurrency budgets, including failed attempts and retries.
- [ ] Limit critic revisions to two; return explicit partial results when budgets expire.
- [ ] Support quality-incident routing and checkpoint pause/resume for later approval integration.

**Done when:** fixed-input workflows exercise basic BI, revenue investigation and the quality incident. Quality blockers stop commercial inference; budget exhaustion terminates; interrupted runs resume without losing evidence or repeating completed side effects.

**References:** [agent routing](03-agent-architecture.md), [execution budgets](../config/base.yaml), [scenarios A–C](15-demo-scenarios.md).

## Stage 6 — API, jobs and approvals

**Goal:** expose durable analysis runs to authenticated users.


- [ ] Add application migrations for users, runs, approvals, audit logs, evidence and checkpoints.
- [ ] Implement FastAPI authentication and server-side viewer, analyst and approver permissions.
- [ ] Add run submission/status/history and authorized evidence, SQL, chart and trace retrieval.
- [ ] Connect Celery/Redis workers using run IDs for idempotency and durable state independent of queue delivery.
- [ ] Implement approval previews and decisions bound to actor, run, operation, resource and exact content hash; enforce expiry, invalidation, denial and audited resume.

**Done when:** API integration tests demonstrate role isolation, durable jobs, queue redelivery safety, denied/expired approvals and changed-content rejection. Worker restarts preserve completed results and approval state.

**References:** [system architecture](02-architecture.md), [security and approvals](11-security.md).

## Stage 7 — Web workspace

**Goal:** let a user ask, inspect and approve through the application.

- [ ] Build the Next.js workspace: login, question submission, progress, run history and error/partial-result states.
- [ ] Present reports, charts, executed SQL, metric versions, evidence and agent traces.
- [ ] Show exact proposed changes and validation results before approval; display expiry and permission restrictions.
- [ ] Provide keyboard navigation, labeled controls and accessible loading/error feedback.

**Done when:** browser checks cover login → question → result → SQL/evidence/chart inspection, plus approval denial/expiry and unauthorized access. Scenarios A–C work through the UI with visible limitations and provenance.

**References:** [product acceptance](01-product-overview.md), [demo scenarios](15-demo-scenarios.md).

## Stage 8 — dbt engineering and GitHub PR workflow

**Goal:** complete scenario D with a reviewable, approved change.

- [ ] Inspect existing customer/month models and propose the smallest model/tests needed for observed cumulative customer revenue.
- [ ] Generate a concrete diff and compile/test it in an isolated environment under the existing policy; run the critic before presenting it.
- [ ] Show the exact diff, test results, target repository and intended mutations in the approval preview.
- [ ] After bound human approval, create the branch, files, commit and PR through scoped GitHub tools, recording outcomes for replay safety.
- [ ] Require new approval for changed content and separate authorization for production model execution; prohibit automatic merges.

**Done when:** scenario D produces a tested PR matching the approved content. Denial, expiry, changed content and retries are exercised without unauthorized or duplicate writes. The model includes zero-activity carry-forward and is labeled historical observed value, not predicted profit.

**References:** [scenario D](15-demo-scenarios.md), [approval policy](11-security.md), [MCP contracts](07-mcp-architecture.md).

## Stage 9 — Observability, security and recovery

**Goal:** prove that the integrated system remains bounded and recoverable under failure.

- [ ] Connect LangSmith and OpenTelemetry traces; expose Prometheus metrics and Grafana dashboards for reliability, quality, accuracy, latency and cost.
- [ ] Verify correlation IDs, sensitive-data redaction, restricted evidence access and configured retention.
- [ ] Add alerts for queue delays, failed jobs, database health, slow queries, stale assets and exhausted budgets.
- [ ] Exercise DB/Redis outages, provider timeouts, schema drift, missing data, dbt failures and telemetry export failures.
- [ ] Verify rate limits, secret handling and authentication/CSRF/session controls appropriate to the chosen auth mechanism.

**Done when:** failures yield explicit durable outcomes, no silent result loss and no duplicate external mutations. Alerts fire under controlled faults; recovery procedures are documented and exercised; required security regression checks pass.

**References:** [observability](10-observability.md), [security](11-security.md), [testing](12-testing-strategy.md).

## Stage 10 — Evaluations and release gate

**Goal:** measure the actual agents against the frozen expectations.

- [ ] Run the 100-case suite against the implemented workflow and all 25 golden cases against their frozen synthetic dataset.
- [ ] Measure numeric/SQL accuracy, tool/metric selection, routing, groundedness, critic revisions, completion, latency, tokens and cost.
- [ ] Evaluate behavioral/statistical cases with explicit assertions; review judge disagreements without allowing a judge to override numeric/security failures.
- [ ] Publish results and fix regressions; version any intentional fixture/metric expectation changes explicitly.

**Done when:** all golden results and permission/SQL negative tests pass, golden answers contain no unsupported numeric claims, and quality blockers are recognized. The wider suite meets the planned targets of at least 95% numeric accuracy and 90% completion; latency/cost percentiles and remaining limitations are published.

**Reference:** [evaluation plan](09-agent-evaluations.md). These are release targets, not claims of current performance.

## Stage 11 — Deployment and demo handoff

**Goal:** deliver a reproducible, operable V1 after the release gate passes.

- [ ] Build immutable images and extend Compose to the implemented services; configure EC2, Nginx HTTPS and restricted internal networking.
- [ ] Supply production secrets securely, configure budget/health/certificate alerts and deploy through the approved release process.
- [ ] Verify migrations, readiness, image rollback and encrypted off-host backups for both databases.
- [ ] Restore a backup and demonstrate the planned 24-hour RPO and 4-hour RTO; document the monthly restore check.
- [ ] Finish working setup/development commands, operator runbooks and reproducible walkthroughs for all four demos.

**Done when:** deployment smoke checks pass, backup restore and rollback are demonstrated, private services are not publicly reachable, and a fresh setup can reproduce the documented demos. State the accepted single-host availability limit.

**References:** [deployment design](14-aws-deployment.md), [local development](13-local-development.md), [demo scenarios](15-demo-scenarios.md).

## Working rule

Keep each implementation change small enough to review with its relevant test evidence. Update this roadmap's status only after the stage gate passes. Multi-tenancy, streaming, additional warehouses, autonomous merges, arbitrary code execution and predictive LTV remain outside V1.
