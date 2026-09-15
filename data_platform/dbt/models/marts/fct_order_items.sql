select order_id, order_item_id, product_id, seller_id, category, purchase_date,
       purchase_month, is_valid, item_price, freight_value
from {{ ref('int_order_items_enriched') }}
