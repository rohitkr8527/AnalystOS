select 'item range' as defect from {{ ref('stg_order_items') }} where item_price < 0 or freight_value < 0
union all
select 'payment range' from {{ ref('stg_payments') }} where payment_value < 0 or payment_installments < 0
union all
select 'review range' from {{ ref('stg_reviews') }} where review_score not between 1 and 5
union all
select 'order status' from {{ ref('stg_orders') }} where order_status not in
  ('created','approved','invoiced','processing','shipped','delivered','canceled','unavailable')
union all
select 'delivery dates' from {{ ref('stg_orders') }} where order_status='delivered'
  and order_delivered_customer_date < order_purchase_timestamp
