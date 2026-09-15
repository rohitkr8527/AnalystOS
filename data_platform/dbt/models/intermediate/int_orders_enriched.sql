with items as (
    select order_id, sum(item_price) as revenue, sum(freight_value) as freight
    from {{ ref('stg_order_items') }} group by order_id
), payments as (
    select order_id, sum(payment_value) as payment_total
    from {{ ref('stg_payments') }} group by order_id
)
select o.order_id, c.customer_unique_id, c.customer_state, c.customer_city,
       o.order_status, o.order_purchase_timestamp,
       o.order_purchase_timestamp::date as purchase_date,
       date_trunc('month', o.order_purchase_timestamp)::date as purchase_month,
       o.order_delivered_customer_date, o.order_estimated_delivery_date,
       o.order_status in ('delivered','shipped','processing','invoiced','approved') as is_valid,
       o.order_status = 'delivered' and o.order_delivered_customer_date is not null
         and o.order_estimated_delivery_date is not null as is_delivered,
       o.order_status = 'delivered' and o.order_delivered_customer_date > o.order_estimated_delivery_date as is_late,
       case when o.order_status = 'delivered'
            then extract(epoch from o.order_delivered_customer_date - o.order_purchase_timestamp) / 86400 end as delivery_days,
       coalesce(i.revenue, 0)::numeric(18,2) as revenue,
       coalesce(i.freight, 0)::numeric(18,2) as freight,
       coalesce(p.payment_total, 0)::numeric(18,2) as payment_total,
       r.review_score
from {{ ref('stg_orders') }} o
join {{ ref('stg_customers') }} c using (customer_id)
left join items i using (order_id)
left join payments p using (order_id)
left join {{ ref('stg_reviews') }} r using (order_id)
