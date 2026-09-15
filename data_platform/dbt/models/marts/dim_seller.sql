select seller_id, seller_state, seller_city from {{ ref('stg_sellers') }}
