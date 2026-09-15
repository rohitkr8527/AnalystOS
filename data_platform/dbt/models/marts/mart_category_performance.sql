select category, purchase_month, sum(item_price)::numeric(18,2) as revenue,
       count(*) as items, count(distinct order_id) as orders
from {{ ref('fct_order_items') }} where is_valid group by category, purchase_month
