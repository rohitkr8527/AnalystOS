select i.order_id, i.order_item_id, i.product_id, i.seller_id,
       coalesce(t.product_category_name_english, 'unknown') as category,
       o.order_purchase_timestamp::date as purchase_date,
       date_trunc('month', o.order_purchase_timestamp)::date as purchase_month,
       o.order_status in ('delivered','shipped','processing','invoiced','approved') as is_valid,
       i.item_price, i.freight_value
from {{ ref('stg_order_items') }} i
join {{ ref('stg_orders') }} o using (order_id)
join {{ ref('stg_products') }} p using (product_id)
left join {{ ref('stg_product_category_translation') }} t using (product_category_name)
