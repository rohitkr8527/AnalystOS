# Governed metrics

[Metric definitions](../src/analystos/features/metrics/definitions/core.yaml) are the versioned source of truth. Every metric carries its grain, model, expression, filter, unit, time basis and caveats. Agents select IDs; they cannot redefine expressions.

Valid orders have status delivered, shipped, processing, invoiced or approved. Canceled, unavailable and created orders are excluded. Unknown statuses fail quality until classified. This measures placed valid orders, including ones not delivered; it is not accounting revenue recognition. No refund or cost data is available.

Revenue is sum(item_price), excluding freight. Orders is distinct valid order_id. AOV is revenue / orders, never mean(item_price). Count one row per item; do not multiply by order_item_id. Payments measure paid components and may include freight, so they are not revenue.

Late delivery is strictly delivered_timestamp > estimated_timestamp among delivered orders with both dates. Missing delivered dates on a delivered order fail quality, not a silently reduced denominator. Average review score uses the latest resolved review per delivered order, excludes missing scores and reports review coverage. Repeat rate is customers with at least two valid orders / customers with at least one within the same requested window, using customer_unique_id.

Dates are half-open ranges [start, end). Empty sums/counts return zero; rates/AOV with zero denominator return null, and the report says undefined. Compute currency with decimal precision and round for display only. Percentage metrics use 0–100 units. Distinct counts and ratios cannot be summed across overlapping groups.

Metric changes increment version and require a reviewed diff to definitions, reference queries and golden expectations. A changed expectation is never automatically accepted merely because a new implementation produced it.

