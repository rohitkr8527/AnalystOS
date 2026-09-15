{{ config(severity='warn') }}
select order_id from {{ ref('stg_orders') }} where order_status='delivered'
  and (order_delivered_customer_date is null or order_estimated_delivery_date is null)
