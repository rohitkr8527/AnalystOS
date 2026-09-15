select distinct on (customer_unique_id)
       customer_unique_id, customer_state, customer_city, purchase_date as first_purchase_date
from {{ ref('int_customer_orders') }}
order by customer_unique_id, purchase_date, order_id
