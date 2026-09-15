select p.product_id, coalesce(t.product_category_name_english, 'unknown') as category,
       p.product_weight_g, p.product_length_cm, p.product_height_cm, p.product_width_cm
from {{ ref('stg_products') }} p
left join {{ ref('stg_product_category_translation') }} t using (product_category_name)
