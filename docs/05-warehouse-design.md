# Warehouse and dbt design

The machine-readable [model contracts](../data_platform/dbt/model-contracts.yaml) specify every model's layer, grain, keys and parents. [dbt project configuration](../data_platform/dbt/dbt_project.yml) fixes schema/materialization conventions; the Stage 1 SQL models implement all 31 contracts.

## Layer responsibilities

Staging renames, casts and normalizes source fields. Required-key/parse errors are quarantined with visible counts; do not silently drop suspicious data. Use views. Keep business status exclusions out of staging.

Intermediate models own reusable joins and business flags. First aggregate payments and deduplicated reviews to order grain. Join item sums to orders only after grouping. Customer metrics group by customer_unique_id, not order-specific customer_id. Materialize reusable intermediate models as views initially.

Marts expose dimensions, facts and analytical tables. Materialize tables for predictable reads; full-refresh on this historical dataset. Publish only after dbt tests succeed. All marts document grain and metric version. Agent read access is confined to this layer.

## Facts and dimensions

- dim_customer: one customer_unique_id, canonical state/city from earliest purchase (tie order_id); order-time location remains on fct_orders for regional analysis.
- dim_product: one product_id, translated category or explicit `unknown`, physical attributes.
- dim_seller: one seller_id, state/city, no raw postal observations.
- dim_date: one calendar date across the dataset; include zero-activity dates/months.
- fct_orders: one order_id, customer_unique_id, customer_state, purchase_date/month, status, is_valid, is_delivered, is_late, delivery_days, item revenue, freight, payment total and one review score. Revenue totals do not change when joining this fact to one-to-one dimensions.
- fct_order_items: one (order_id, order_item_id), product/seller keys, category, purchase period, validity, item_price and freight_value.
- fct_payments: one (order_id, payment_sequential), type/installments/value and validity. Never sum item revenue after joining unaggregated payments.

Facts retain invalid-status orders with is_valid=false for quality and reconciliation. Governed revenue/order metrics filter them explicitly. Analytical sales marts include only valid-order contributions; zero periods appear through dim_date. Reviews are nullable, not zero-filled. Category translation misses use `unknown` and surface a warning.

## Analytical marts

Daily/monthly sales: period, revenue, orders, aov, freight and payment totals. Customer metrics: historical spend, first/last order, valid order count and repeat flag. Cohorts: first valid purchase month × activity month, cohort size, active customers and retention. Product/category/seller performance: corresponding key × purchase month, valid item revenue, item count, distinct orders. Delivery performance: delivered purchase month × customer state, eligible deliveries, late count/rate and mean days. Review metrics: purchase month × review score, reviewed delivered orders.

Reconcile sum(fct_order_items.item_price for valid orders) = sum(fct_orders.revenue for valid orders) = sum(mart_monthly_sales.revenue). Payment totals may differ from item revenue; report freight and payment adjustments separately. Multi-category order counts are non-additive across categories.

## dbt execution and tests

Order: raw sources → staging → intermediate → dimensions/facts → analytical marts. `dbt build` will perform transformation and quality checks as one Dagster asset job. Keys use unique/not_null or composite-key tests, FKs use relationships, status values use accepted_values, and custom tests enforce price/date/range/reconciliation rules in [quality policy](../config/data-quality.yaml).
