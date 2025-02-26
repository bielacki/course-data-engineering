{{ config(materialized='table') }}

with group_by_quarter as (
  select
    service_type,
    extract(year from pickup_datetime) as year,
    extract(quarter from pickup_datetime) as quarter,
    sum(total_amount) as total_amount
  from
    {{ ref("fact_trips") }}
  group by all
),

calculate_prev_year_reve as (
  select
    service_type,
    year,
    quarter,
    total_amount,
    lag(total_amount, 4) over (partition by service_type order by year, quarter) as total_amount_prev_year
  from group_by_quarter
),

final as (
  select
    *,
    (safe_divide(total_amount, total_amount_prev_year) - 1) * 100 as yoy_growth
  from calculate_prev_year_reve
  order by service_type, year desc, quarter desc
)

select * from final
