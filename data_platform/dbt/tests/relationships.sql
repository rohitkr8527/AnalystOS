select 'orders.customer_id' as defect
from {{ ref('stg_orders') }} o left join {{ ref('stg_customers') }} c using (customer_id)
where c.customer_id is null
union all
select 'items.order_id' from {{ ref('stg_order_items') }} i left join {{ ref('stg_orders') }} o using (order_id)
where o.order_id is null
union all
select 'items.product_id' from {{ ref('stg_order_items') }} i left join {{ ref('stg_products') }} p using (product_id)
where p.product_id is null
union all
select 'items.seller_id' from {{ ref('stg_order_items') }} i left join {{ ref('stg_sellers') }} s using (seller_id)
where s.seller_id is null
union all
select 'payments.order_id' from {{ ref('stg_payments') }} p left join {{ ref('stg_orders') }} o using (order_id)
where o.order_id is null
union all
select 'reviews.order_id' from {{ ref('stg_reviews') }} r left join {{ ref('stg_orders') }} o using (order_id)
where o.order_id is null
