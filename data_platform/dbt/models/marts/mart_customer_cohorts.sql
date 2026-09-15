with valid as (
    select customer_unique_id, purchase_month from {{ ref('fct_orders') }} where is_valid
), cohorts as (
    select customer_unique_id, min(purchase_month) as cohort_month from valid group by customer_unique_id
), activity as (
    select c.cohort_month, v.purchase_month as activity_month, count(distinct v.customer_unique_id) as active_customers
    from valid v join cohorts c using (customer_unique_id) group by c.cohort_month, v.purchase_month
), sizes as (
    select cohort_month, count(*) as cohort_size from cohorts group by cohort_month
)
select a.cohort_month, a.activity_month, s.cohort_size, a.active_customers,
       a.active_customers::numeric / nullif(s.cohort_size, 0) as retention_rate
from activity a join sizes s using (cohort_month)
