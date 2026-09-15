# Product scope — frozen V1

AnalystOS answers business questions with governed metrics, safe read-only SQL, statistical analysis, charts and evidence-backed reports. It also proposes dbt models and tests through an approved GitHub pull request.

## Acceptance boundary

One Olist warehouse, one organization, BRL, historical batch data, seven agents and three MCP servers. V1 supports the four scenarios in [demo scenarios](15-demo-scenarios.md). Every numeric claim links to query results, metric version and source models. Quality failures can stop an investigation. The app exposes run history, SQL, charts, evidence, agent traces and approvals.

Analytical revenue means valid-order item value, not profit or accounting-recognized revenue. No advertising, acquisition cost, inventory or refund facts exist; do not infer them. Historical customer value is observable; future LTV prediction is out of scope.

## Deferred scope

Multi-tenancy, additional warehouses, live streaming, autonomous merges/deploys, warehouse writes by agents, arbitrary Python execution, Kubernetes and automated predictive LTV are outside V1. Authentication, least privilege, validation, audit, bounded retries and accessibility remain required before production.

Scope changes require an updated design decision, impacted contracts and regression expectations in the same change. This baseline is the user's attached plan, implemented on 2026-09-16.

