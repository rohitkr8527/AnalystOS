with ranked as (
    select *, row_number() over (
        partition by order_id
        order by review_answer_timestamp desc nulls last,
                 review_creation_date desc nulls last, review_id desc
    ) as position
    from {{ source('olist', 'reviews') }}
)
select review_id, order_id, review_score, review_creation_date, review_answer_timestamp
from ranked where position = 1
