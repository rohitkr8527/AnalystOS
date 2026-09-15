select date_trunc('month', purchase_date)::date as purchase_month,
       sum(revenue)::numeric(18,2) as revenue, sum(orders)::bigint as orders,
       coalesce(sum(revenue) / nullif(sum(orders), 0), 0)::numeric(18,2) as average_order_value,
       sum(freight)::numeric(18,2) as freight, sum(payment_total)::numeric(18,2) as payment_total
from {{ ref('mart_daily_sales') }} group by date_trunc('month', purchase_date)::date
