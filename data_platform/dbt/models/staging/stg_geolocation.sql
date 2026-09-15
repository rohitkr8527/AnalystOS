select geolocation_zip_code_prefix,
       percentile_cont(0.5) within group (order by geolocation_lat) as latitude,
       percentile_cont(0.5) within group (order by geolocation_lng) as longitude,
       min(geolocation_city) as city, min(geolocation_state) as state
from {{ source('olist', 'geolocation') }}
group by geolocation_zip_code_prefix
