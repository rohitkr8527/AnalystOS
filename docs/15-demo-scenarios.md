# Four fixed demo scenarios

## A — Basic BI

Question: “What were our top five categories by revenue in January 2018?” Resolve revenue v1, read category/month mart, sort revenue descending then category ascending, return top five or all available when fewer exist. Include BRL, validity filter, period, SQL and evidence. Synthetic expected category totals are frozen in the golden set; Olist values are measured after warehouse build.

## B — Revenue investigation

Question: “Revenue dropped from January to February 2018. Why?” Check completeness first, quantify month totals and change, decompose by category/state/seller and distinguish order volume from AOV. Category contributions reconcile to the total change. Return descriptive drivers with evidence, not causal claims about marketing or competition. Fixed synthetic data intentionally reduces item values in February; real Olist periods do not assume a decline until verified.

## C — Data-quality incident

Question: “Orders fell at the end of March 2018. Why?” Use `stale_pipeline`, logical as_of 2018-03-31, incomplete batch watermark 2018-03-15. Identify missing expected period coverage before generating a commercial narrative. Stop the decline inference, report the pipeline/watermark evidence and recommend restoring/rechecking data. Complete archival data is not stale merely because it is historical.

## D — Analytics engineering

Question: “Build a reusable monthly customer LTV model.” Clarify the output as observed cumulative valid item revenue per customer_unique_id through each calendar month, with zero-activity carry-forward, first purchase and valid order count. Do not label it predicted lifetime profit. Inspect existing customer/month models, propose the minimal dbt model and schema tests, compile and run tests in an isolated environment, critique, present a concrete diff and seek approval, then create a GitHub PR. No merge or production run without separate authorization.

