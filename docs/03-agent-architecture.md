# Seven agent contracts — frozen

| Agent | Inputs | Outputs and responsibility | Permitted tools |
| --- | --- | --- | --- |
| Analytics Manager | Question, actor, budgets, run state | Resolve intent/time window, plan/delegate, track budgets, bounded revisions, assemble response | Metric/catalog lookup, delegate, approval request, report assembly |
| Metadata | Business entities and candidate metrics | Vetted tables, columns, joins, lineage, metric IDs; flag ambiguity | Catalog, metric lookup, dbt metadata |
| Data Quality | Selected models, period, batch watermark | Passed/failed rules, affected scope, stop/warn decision | Quality checks, freshness metadata, approved dbt test runner |
| SQL Analyst | Plan, resolved metrics, vetted schema | SQL proposal, bindings, grain, assumptions | Catalog, metric lookup; submit SQL to controlled validator |
| Statistical Analyst | Bounded query results, statistical plan | Effect size, uncertainty, assumptions and limitations | Registered statistics tools; no arbitrary code |
| Business Analyst | Evidence and statistics | Ranked findings with evidence IDs and recommendations | Evidence lookup; cannot invent causes |
| Critic | Claims, SQL, metrics and evidence | Accept or request targeted revision; detect fanout, weak inference and unsupported claims | Evidence/catalog/metric read; no mutations |

Visualization is a deterministic service. SQL Analyst does not execute SQL: the shared tool executor validates and authorizes every query. The Manager invokes registered tools using the requesting actor's scope; delegation never broadens it.

Workflow state contract: run_id, user_id, question, as_of, requested_period, plan, metric_ids, candidate_tables, quality_results, sql_proposals, query_ids, evidence_ids, findings, critic_revision_count, budget_usage, approval_ids, status and error. Large result sets live in evidence storage, not prompts/checkpoints.

Routing: resolve intent → metadata/metrics → quality gate → plan → SQL validation/execution → statistics if justified → business interpretation → critic → deterministic chart/report. Quality errors route to an incident report. Critic can loop at most twice; exhausted budgets return a partial report with explicit gaps. Persist before human approval and resume only with a bound approval record.

