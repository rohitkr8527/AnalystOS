select product_id, order_id, purchase_month,
       sum(item_price) filter (where is_valid) as revenue,
       count(*) filter (where is_valid) as items
from {{ ref('int_order_items_enriched') }}
group by product_id, order_id, purchase_month
