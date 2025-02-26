## Module 4 Homework: Analytics Engineering

Let's check if numbers in our datasets match with numbers from homework "Before you start" section.

```sql
select count(*) from `course-data-engineering.de_zoomcamp.source_fhv_tripdata`;
select count(*) from `course-data-engineering.de_zoomcamp.source_yellow_tripdata`;
select count(*) from `course-data-engineering.de_zoomcamp.source_green_tripdata`;
```

Output:
```
43244696
109047518
7778101
```

All good.

### Question 1: Understanding dbt model resolution

Provided you've got the following sources.yaml
```yaml
version: 2

sources:
  - name: raw_nyc_tripdata
    database: "{{ env_var('DBT_BIGQUERY_PROJECT', 'dtc_zoomcamp_2025') }}"
    schema:   "{{ env_var('DBT_BIGQUERY_SOURCE_DATASET', 'raw_nyc_tripdata') }}"
    tables:
      - name: ext_green_taxi
      - name: ext_yellow_taxi
```

with the following env variables setup where `dbt` runs:
```shell
export DBT_BIGQUERY_PROJECT=myproject
export DBT_BIGQUERY_DATASET=my_nyc_tripdata
```

What does this .sql model compile to?
```sql
select * 
from {{ source('raw_nyc_tripdata', 'ext_green_taxi' ) }}
```

- `select * from dtc_zoomcamp_2025.raw_nyc_tripdata.ext_green_taxi`
- `select * from dtc_zoomcamp_2025.my_nyc_tripdata.ext_green_taxi`
- `select * from myproject.raw_nyc_tripdata.ext_green_taxi`
- `select * from myproject.my_nyc_tripdata.ext_green_taxi`
- `select * from dtc_zoomcamp_2025.raw_nyc_tripdata.green_taxi`


#### Solution 1:

Database in dbt is project in BigQuery.
Schema in dbt is dataset in BigQuery.

`env_var` in dbt accepts a second, optional argument for default value to avoid compilation errors when the environment variable isn't available.

So, in a compiled code:
- project name will be `myproject` (from the DBT_BIGQUERY_PROJECT env variable)
- dataset name will be `raw_nyc_tripdata` because this is the fallback value (env vars in the `yml` file and in the shell command are different)
- table name will be  `ext_green_taxi`


#### Answer 1:

```sql
select * from myproject.raw_nyc_tripdata.ext_green_taxi
```

### Question 2: dbt Variables & Dynamic Models

Say you have to modify the following dbt_model (`fct_recent_taxi_trips.sql`) to enable Analytics Engineers to dynamically control the date range. 

- In development, you want to process only **the last 7 days of trips**
- In production, you need to process **the last 30 days** for analytics

```sql
select *
from {{ ref('fact_taxi_trips') }}
where pickup_datetime >= CURRENT_DATE - INTERVAL '30' DAY
```

What would you change to accomplish that in a such way that command line arguments takes precedence over ENV_VARs, which takes precedence over DEFAULT value?

- Add `ORDER BY pickup_datetime DESC` and `LIMIT {{ var("days_back", 30) }}`
- Update the WHERE clause to `pickup_datetime >= CURRENT_DATE - INTERVAL '{{ var("days_back", 30) }}' DAY`
- Update the WHERE clause to `pickup_datetime >= CURRENT_DATE - INTERVAL '{{ env_var("DAYS_BACK", "30") }}' DAY`
- Update the WHERE clause to `pickup_datetime >= CURRENT_DATE - INTERVAL '{{ var("days_back", env_var("DAYS_BACK", "30")) }}' DAY`
- Update the WHERE clause to `pickup_datetime >= CURRENT_DATE - INTERVAL '{{ env_var("DAYS_BACK", var("days_back", "30")) }}' DAY`

#### Solution 2:

This Jinja macro `{{ var("days_back", env_var("DAYS_BACK", "30")) }}` does exactly what's needed. 

#### Answer 2:

Update the WHERE clause to `pickup_datetime >= CURRENT_DATE - INTERVAL '{{ var("days_back", env_var("DAYS_BACK", "30")) }}' DAY`

### Question 3: dbt Data Lineage and Execution

Considering the data lineage below **and** that taxi_zone_lookup is the **only** materialization build (from a .csv seed file):

![image](./homework_q2.png)

Select the option that does **NOT** apply for materializing `fct_taxi_monthly_zone_revenue`:

- `dbt run`
- `dbt run --select +models/core/dim_taxi_trips.sql+ --target prod`
- `dbt run --select +models/core/fct_taxi_monthly_zone_revenue.sql`
- `dbt run --select +models/core/`
- `dbt run --select models/staging/+`

#### Solution 3:

- ❌ `dbt run` runs all models
- ❌ `dbt run --select +models/core/dim_taxi_trips.sql+ --target prod` runs dim_taxi_trips and all ancestors and descendants.
- ❌ `dbt run --select +models/core/fct_taxi_monthly_zone_revenue.sql` runs fct_taxi_monthly_zone_revenue and all ancestors.
- ❌ `dbt run --select +models/core/` runs all models in core and ancestors.
- ✅ `dbt run --select models/staging/+` this will run all models in staging and descendants. dim_zone_lookup is in the core folder and doesn't depend on staging models. But fct_taxi_monthly_zone_revenue depends on dim_zone_lookup, so it won't be materialized.

#### Answer 3:

`dbt run --select models/staging/+`

### Question 4: dbt Macros and Jinja

Consider you're dealing with sensitive data (e.g.: [PII](https://en.wikipedia.org/wiki/Personal_data)), that is **only available to your team and very selected few individuals**, in the `raw layer` of your DWH (e.g: a specific BigQuery dataset or PostgreSQL schema), 

 - Among other things, you decide to obfuscate/masquerade that data through your staging models, and make it available in a different schema (a `staging layer`) for other Data/Analytics Engineers to explore

- And **optionally**, yet  another layer (`service layer`), where you'll build your dimension (`dim_`) and fact (`fct_`) tables (assuming the [Star Schema dimensional modeling](https://www.databricks.com/glossary/star-schema)) for Dashboarding and for Tech Product Owners/Managers

You decide to make a macro to wrap a logic around it:

```sql
{% macro resolve_schema_for(model_type) -%}

    {%- set target_env_var = 'DBT_BIGQUERY_TARGET_DATASET'  -%}
    {%- set stging_env_var = 'DBT_BIGQUERY_STAGING_DATASET' -%}

    {%- if model_type == 'core' -%} {{- env_var(target_env_var) -}}
    {%- else -%}                    {{- env_var(stging_env_var, env_var(target_env_var)) -}}
    {%- endif -%}

{%- endmacro %}
```

And use on your staging, dim_ and fact_ models as:
```sql
{{ config(
    schema=resolve_schema_for('core'), 
) }}
```

That all being said, regarding macro above, **select all statements that are true to the models using it**:
- Setting a value for  `DBT_BIGQUERY_TARGET_DATASET` env var is mandatory, or it'll fail to compile
- Setting a value for `DBT_BIGQUERY_STAGING_DATASET` env var is mandatory, or it'll fail to compile
- When using `core`, it materializes in the dataset defined in `DBT_BIGQUERY_TARGET_DATASET`
- When using `stg`, it materializes in the dataset defined in `DBT_BIGQUERY_STAGING_DATASET`, or defaults to `DBT_BIGQUERY_TARGET_DATASET`
- When using `staging`, it materializes in the dataset defined in `DBT_BIGQUERY_STAGING_DATASET`, or defaults to `DBT_BIGQUERY_TARGET_DATASET`


#### Solution 4:

- ✅ Setting a value for `DBT_BIGQUERY_TARGET_DATASET` env var is mandatory, or it'll fail to compile
- ❌ Setting a value for `DBT_BIGQUERY_STAGING_DATASET` env var is mandatory, or it'll fail to compile - nope, because there is a fallback - env_var(target_env_var)
- ✅ When using `core`, it materializes in the dataset defined in `DBT_BIGQUERY_TARGET_DATASET`
- ✅ When using `stg`, it materializes in the dataset defined in `DBT_BIGQUERY_STAGING_DATASET`, or defaults to `DBT_BIGQUERY_TARGET_DATASET`
- ✅ When using `staging`, it materializes in the dataset defined in `DBT_BIGQUERY_STAGING_DATASET`, or defaults to `DBT_BIGQUERY_TARGET_DATASET`


## Serious SQL

Alright, in module 1, you had a SQL refresher, so now let's build on top of that with some serious SQL.

These are not meant to be easy - but they'll boost your SQL and Analytics skills to the next level.  
So, without any further do, let's get started...

You might want to add some new dimensions `year` (e.g.: 2019, 2020), `quarter` (1, 2, 3, 4), `year_quarter` (e.g.: `2019/Q1`, `2019-Q2`), and `month` (e.g.: 1, 2, ..., 12), **extracted from pickup_datetime**, to your `fct_taxi_trips` OR `dim_taxi_trips.sql` models to facilitate filtering your queries


### Question 5: Taxi Quarterly Revenue Growth

1. Create a new model `fct_taxi_trips_quarterly_revenue.sql`
2. Compute the Quarterly Revenues for each year for based on `total_amount`
3. Compute the Quarterly YoY (Year-over-Year) revenue growth 
  * e.g.: In 2020/Q1, Green Taxi had -12.34% revenue growth compared to 2019/Q1
  * e.g.: In 2020/Q4, Yellow Taxi had +34.56% revenue growth compared to 2019/Q4

Considering the YoY Growth in 2020, which were the yearly quarters with the best (or less worse) and worst results for green, and yellow

- green: {best: 2020/Q2, worst: 2020/Q1}, yellow: {best: 2020/Q2, worst: 2020/Q1}
- green: {best: 2020/Q2, worst: 2020/Q1}, yellow: {best: 2020/Q3, worst: 2020/Q4}
- green: {best: 2020/Q1, worst: 2020/Q2}, yellow: {best: 2020/Q2, worst: 2020/Q1}
- green: {best: 2020/Q1, worst: 2020/Q2}, yellow: {best: 2020/Q1, worst: 2020/Q2}
- green: {best: 2020/Q1, worst: 2020/Q2}, yellow: {best: 2020/Q3, worst: 2020/Q4}

#### Solution 5:

First, let's create a `fct_taxi_trips_quarterly_revenue.sql` model to calculate quarterly revenue and growth YoY:

```sql
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
```

Then we can query this table:

```sql
select
  service_type,
  year,
  quarter,
  yoy_growth
from
  `course-data-engineering.de_zoomcamp.fct_taxi_trips_quarterly_revenue`
where
  year = 2020
group by all
order by service_type, year desc, quarter desc
```

And find the answer in the results.
Alternatively, we can write the following query, and get the answer in a form of a table:

```sql
select
  service_type,
  year,
  max_by(quarter, yoy_growth) as max_growth_quarter,
  min_by(quarter, yoy_growth) as min_growth_quarter
from
  `course-data-engineering.de_zoomcamp.fct_taxi_trips_quarterly_revenue`
where
  year = 2020
group by all
```

Output:

| service_type  | year  | max_growth_quarter  | min_growth_quarter  |
|---|---|---|---|
|  Green |  2020 |  1 |  2 |
|  Yellow |  2020 | 1  |  2 |


#### Answer 5:

- green: {best: 2020/Q1, worst: 2020/Q2}, yellow: {best: 2020/Q1, worst: 2020/Q2}

### Question 6: P97/P95/P90 Taxi Monthly Fare

1. Create a new model `fct_taxi_trips_monthly_fare_p95.sql`
2. Filter out invalid entries (`fare_amount > 0`, `trip_distance > 0`, and `payment_type_description in ('Cash', 'Credit Card')`)
3. Compute the **continous percentile** of `fare_amount` partitioning by service_type, year and and month

Now, what are the values of `p97`, `p95`, `p90` for Green Taxi and Yellow Taxi, in April 2020?

- green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 52.0, p95: 37.0, p90: 25.5}
- green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 31.5, p95: 25.5, p90: 19.0}
- green: {p97: 40.0, p95: 33.0, p90: 24.5}, yellow: {p97: 52.0, p95: 37.0, p90: 25.5}
- green: {p97: 40.0, p95: 33.0, p90: 24.5}, yellow: {p97: 31.5, p95: 25.5, p90: 19.0}
- green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 52.0, p95: 25.5, p90: 19.0}

#### Solution 6:

Let's create a `fct_taxi_trips_monthly_fare_p95.sql` model:

```sql
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
```

Build the model:

```bash
dbt build -s fct_taxi_trips_monthly_fare_p95
```

And query final table in BigQuery:

```sql
select
  *
from
  `course-data-engineering.de_zoomcamp.fct_taxi_trips_monthly_fare_p95`
where
  pickup_year = 2020
  and pickup_month = 4
```

Output:

|  service_type | pickup_year  | pickup_month  | p97  | p95  | p90  |
|---|---|---|---|---|---|
| Green  | 2020  | 4  | 55.0  | 45.0  | 26.5  |
| Yellow | 2020  | 4  | 31.5  | 25.5  | 19.0  |


#### Answer 6:

green: {p97: 55.0, p95: 45.0, p90: 26.5}, yellow: {p97: 31.5, p95: 25.5, p90: 19.0}

### Question 7: Top #Nth longest P90 travel time Location for FHV

Prerequisites:
* Create a staging model for FHV Data (2019), and **DO NOT** add a deduplication step, just filter out the entries where `where dispatching_base_num is not null`
* Create a core model for FHV Data (`dim_fhv_trips.sql`) joining with `dim_zones`. Similar to what has been done [here](../../../04-analytics-engineering/taxi_rides_ny/models/core/fact_trips.sql)
* Add some new dimensions `year` (e.g.: 2019) and `month` (e.g.: 1, 2, ..., 12), based on `pickup_datetime`, to the core model to facilitate filtering for your queries

Now...
1. Create a new model `fct_fhv_monthly_zone_traveltime_p90.sql`
2. For each record in `dim_fhv_trips.sql`, compute the [timestamp_diff](https://cloud.google.com/bigquery/docs/reference/standard-sql/timestamp_functions#timestamp_diff) in seconds between dropoff_datetime and pickup_datetime - we'll call it `trip_duration` for this exercise
3. Compute the **continous** `p90` of `trip_duration` partitioning by year, month, pickup_location_id, and dropoff_location_id

For the Trips that **respectively** started from `Newark Airport`, `SoHo`, and `Yorkville East`, in November 2019, what are **dropoff_zones** with the 2nd longest p90 trip_duration ?

- LaGuardia Airport, Chinatown, Garment District
- LaGuardia Airport, Park Slope, Clinton East
- LaGuardia Airport, Saint Albans, Howard Beach
- LaGuardia Airport, Rosedale, Bath Beach
- LaGuardia Airport, Yorkville East, Greenpoint

#### Solution 7:

Let's create a `stg_fhv_tripdata` staging model:

```sql
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
```

Build:

```bash
dbt build -s stg_fhv_tripdata
```

Create a `dim_fhv_trips` model:

```sql
{{ config(materialized='table') }}

with fhv_tripdata as (
    select * from {{ ref("stg_fhv_tripdata") }}
), 

dim_zones as (
    select * from {{ ref('dim_zones') }}
    where borough != 'Unknown'
)

select
    fhv_tripdata.tripid,
    fhv_tripdata.dispatching_base_num,
    fhv_tripdata.affiliated_base_number,
    fhv_tripdata.sr_flag,
    extract(year from fhv_tripdata.pickup_datetime) as pickup_year,
    extract(month from fhv_tripdata.pickup_datetime) as pickup_month,
    fhv_tripdata.pickup_datetime, 
    fhv_tripdata.dropoff_datetime, 
    fhv_tripdata.pickup_locationid, 
    pickup_zone.borough as pickup_borough, 
    pickup_zone.zone as pickup_zone, 
    fhv_tripdata.dropoff_locationid,
    dropoff_zone.borough as dropoff_borough, 
    dropoff_zone.zone as dropoff_zone
from fhv_tripdata
inner join dim_zones as pickup_zone
    on fhv_tripdata.pickup_locationid = pickup_zone.locationid
inner join dim_zones as dropoff_zone
    on fhv_tripdata.dropoff_locationid = dropoff_zone.locationid
```

Materialize a table:

```bash
dbt run -s dim_fhv_trips
```

Create a `fct_fhv_monthly_zone_traveltime_p90` model:

```sql
{{ config(materialized='table') }}

with fhv_trips as (
  select
    *,
    timestamp_diff(dropoff_datetime, pickup_datetime, second) as trip_duration,
  from
    {{ ref("dim_fhv_trips") }}
),

percentiles as (
  select
    *,
    percentile_cont(trip_duration, 0.90) over (partition by pickup_year, pickup_month, pickup_locationid, dropoff_locationid) as p90,
from
  fhv_trips
)

select * from percentiles
```

Materialize the model:

```bash
dbt run -s fct_fhv_monthly_zone_traveltime_p90
```

Now we can query the table:

```sql
with filtered as (
  select
    pickup_year,
    pickup_month,
    pickup_zone,
    dropoff_zone,
    p90,
  from `course-data-engineering.de_zoomcamp.fct_fhv_monthly_zone_traveltime_p90`
  where
    lower(pickup_zone) in ('newark airport', 'soho', 'yorkville east')
    and pickup_year = 2019
    and pickup_month = 11
  group by all
),

ranked as (
  select
    *,
    row_number() over (partition by pickup_zone order by p90 desc) as p90_rank
  from filtered
)

select * from ranked where p90_rank = 2
```

Output:

|  pickup_year | pickup_month  | pickup_zone  | dropoff_zone  | p90  | p90_rank  |
|---|---|---|---|---|---|
| 2019 | 11  | SoHo  | Chinatown  | 19496.0  | 2  |
| 2019 | 11  | Yorkville East  | Garment District  | 13846.0  | 2  |
| 2019 | 11  | Newark Airport  | LaGuardia Airport | 7028.8000000000011  | 2  |

#### Answer 7:

LaGuardia Airport, Chinatown, Garment District
