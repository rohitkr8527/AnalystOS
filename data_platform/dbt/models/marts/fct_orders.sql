select order_id, customer_unique_id, customer_state, purchase_date, purchase_month,
       order_status, is_valid, is_delivered, is_late, delivery_days,
       revenue, freight, payment_total, review_score
from {{ ref('int_orders_enriched') }}
