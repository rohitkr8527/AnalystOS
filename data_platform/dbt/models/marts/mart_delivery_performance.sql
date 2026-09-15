select purchase_month, customer_state, count(*) as eligible_deliveries,
       count(*) filter (where is_late) as late_deliveries,
       count(*) filter (where is_late)::numeric / nullif(count(*), 0) as late_rate,
       avg(delivery_days)::numeric(18,2) as mean_delivery_days
from {{ ref('fct_orders') }} where is_delivered group by purchase_month, customer_state
