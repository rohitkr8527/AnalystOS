select purchase_month, review_score, count(*) as reviewed_delivered_orders
from {{ ref('fct_orders') }}
where is_delivered and review_score is not null group by purchase_month, review_score
