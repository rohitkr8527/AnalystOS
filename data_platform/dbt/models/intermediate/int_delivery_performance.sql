select order_id, purchase_month, customer_state, is_late, delivery_days
from {{ ref('int_orders_enriched') }} where is_delivered
