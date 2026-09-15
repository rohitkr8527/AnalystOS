select i.seller_id, i.purchase_month, s.seller_state, s.seller_city,
       sum(i.item_price) filter (where i.is_valid) as revenue,
       count(*) filter (where i.is_valid) as items,
       count(distinct i.order_id) filter (where i.is_valid) as orders
from {{ ref('int_order_items_enriched') }} i
join {{ ref('stg_sellers') }} s using (seller_id)
group by i.seller_id, i.purchase_month, s.seller_state, s.seller_city
