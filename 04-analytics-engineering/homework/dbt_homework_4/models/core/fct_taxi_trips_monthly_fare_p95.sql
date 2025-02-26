{{ config(materialized='table') }}

with prep as (
  select
    *,
    extract(year from pickup_datetime) as pickup_year,
    extract(month from pickup_datetime) as pickup_month,
  from
    {{ ref("fact_trips") }}
  where
    fare_amount > 0
    and trip_distance > 0
    and lower(trim(payment_type_description)) in ('cash', 'credit card')
),

percentiles as (
  select
      service_type,
      pickup_year,
      pickup_month,
      percentile_cont(fare_amount, 0.97) over (partition by service_type, pickup_year, pickup_month) as p97,
      percentile_cont(fare_amount, 0.95) over (partition by service_type, pickup_year, pickup_month) as p95,
      percentile_cont(fare_amount, 0.90) over (partition by service_type, pickup_year, pickup_month) as p90,
  from prep
)

select
  *
from
  percentiles
group by
  all
order by
  service_type,
  pickup_year asc,
  pickup_year asc