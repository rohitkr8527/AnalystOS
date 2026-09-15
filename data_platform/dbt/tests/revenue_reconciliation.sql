with totals as (
  select (select coalesce(sum(item_price), 0) from {{ ref('fct_order_items') }} where is_valid) as items,
         (select coalesce(sum(revenue), 0) from {{ ref('fct_orders') }} where is_valid) as orders,
         (select coalesce(sum(revenue), 0) from {{ ref('mart_monthly_sales') }}) as months
)
select * from totals where abs(items - orders) > 0.01 or abs(orders - months) > 0.01
