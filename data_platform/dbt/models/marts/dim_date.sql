select day::date as date_day,
       date_trunc('month', day)::date as month_start,
       extract(year from day)::integer as year,
       extract(month from day)::integer as month,
       extract(day from day)::integer as day_of_month
from generate_series(
    (select min(order_purchase_timestamp)::date from {{ ref('stg_orders') }}),
    (select max(order_purchase_timestamp)::date from {{ ref('stg_orders') }}),
    interval '1 day'
) day
