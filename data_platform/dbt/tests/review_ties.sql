select order_id, review_answer_timestamp, review_creation_date
from {{ source('olist', 'reviews') }}
group by order_id, review_answer_timestamp, review_creation_date
having count(distinct (review_id, review_score, review_comment_title, review_comment_message)) > 1
