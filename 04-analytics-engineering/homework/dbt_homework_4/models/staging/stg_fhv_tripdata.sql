{{ config(materialized='view') }}

select
  dispatching_base_num,
  affiliated_base_number,
  {{ dbt_utils.generate_surrogate_key(['dispatching_base_num', 'pickup_datetime']) }} as tripid,
  {{ dbt.safe_cast("PUlocationID", api.Column.translate_type("integer")) }} as pickup_locationid,
  {{ dbt.safe_cast("DOlocationID", api.Column.translate_type("integer")) }} as dropoff_locationid,
  sr_flag,

  -- timestamps
  cast(pickup_datetime as timestamp) as pickup_datetime,
  cast(dropOff_datetime as timestamp) as dropoff_datetime,
from
  {{ source('staging','source_fhv_tripdata') }}
where
  dispatching_base_num is not null
