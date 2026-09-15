select order_id, customer_unique_id, customer_state, customer_city, purchase_date,
       purchase_month, is_valid, revenue
from {{ ref('int_orders_enriched') }}
