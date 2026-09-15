select d.date_day as purchase_date,
       coalesce(sum(o.revenue) filter (where o.is_valid), 0)::numeric(18,2) as revenue,
       count(o.order_id) filter (where o.is_valid) as orders,
       coalesce(sum(o.revenue) filter (where o.is_valid) /
                nullif(count(o.order_id) filter (where o.is_valid), 0), 0)::numeric(18,2) as average_order_value,
       coalesce(sum(o.freight) filter (where o.is_valid), 0)::numeric(18,2) as freight,
       coalesce(sum(o.payment_total) filter (where o.is_valid), 0)::numeric(18,2) as payment_total
from {{ ref('dim_date') }} d
left join {{ ref('fct_orders') }} o on o.purchase_date = d.date_day
group by d.date_day
