select d.customer_unique_id,
       coalesce(sum(o.revenue) filter (where o.is_valid), 0)::numeric(18,2) as historical_spend,
       min(o.purchase_date) filter (where o.is_valid) as first_order_date,
       max(o.purchase_date) filter (where o.is_valid) as last_order_date,
       count(distinct o.order_id) filter (where o.is_valid) as valid_orders,
       count(distinct o.order_id) filter (where o.is_valid) > 1 as is_repeat_customer
from {{ ref('dim_customer') }} d
left join {{ ref('fct_orders') }} o using (customer_unique_id)
group by d.customer_unique_id
