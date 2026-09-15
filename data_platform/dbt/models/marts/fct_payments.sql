select p.order_id, p.payment_sequential, p.payment_type, p.payment_installments,
       p.payment_value, o.purchase_date, o.purchase_month, o.is_valid
from {{ ref('stg_payments') }} p join {{ ref('fct_orders') }} o using (order_id)
