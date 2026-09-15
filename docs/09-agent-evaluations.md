# Evaluation plan

[cases.json](../evaluations/cases/cases.json) contains exactly 100 planned cases: 20 aggregation, 20 filtering/grouping, 15 joins, 15 trends/comparisons, 10 metric interpretation, 10 root-cause analysis, 5 quality and 5 statistical questions. Each specifies question, difficulty, dataset, expected metric/tables/tools, reference SQL where applicable, expected result or behavioral assertions, and acceptance criteria.

[golden.json](../evaluations/datasets/golden.json) freezes 25 important numeric cases on fixture version 1. The offline verifier executes reference SQL over a synthetic contract warehouse and compares results to these committed expected rows. This verifies benchmark consistency, not agent ability or PostgreSQL/dbt execution.

Root-cause cases require arithmetic contribution attribution and explicit limits on causality. Quality cases must diagnose the fixture defect and block unsupported decline narratives. Statistical cases specify samples, assumptions, effect size and uncertainty; insufficient samples must be acknowledged. A reference SQL of null means behavior/statistics is judged using explicit acceptance assertions, not SQL string matching.

At Stage 10, run agents on these same inputs and record numeric accuracy, SQL execution/semantic accuracy, table/metric/tool selection, routing, groundedness, unsupported claims, critic detection, revision success, completion, latency, token use and cost. Evaluate semantic results rather than exact SQL strings. A judge cannot override numeric/security failures. Human-review disagreements.

Baseline release gate: all 25 golden results pass; all permission/SQL negative tests pass; no unsupported numeric claims in the golden suite; quality blockers are recognized. Wider suite targets: >=95% numeric answer accuracy and >=90% task completion, with latency/cost percentiles published. Targets are planned, not measured agent performance.

Synthetic expected results are immutable until an intentional fixture/metric version change reviewed alongside a diff. Historical Olist benchmarks will be frozen separately against the acquired dataset hash after warehouse implementation.

