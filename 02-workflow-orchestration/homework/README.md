# Module 1 homework: Kestra

2025 cohort questions: [LINK](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2025/02-workflow-orchestration/homework.md)

## Question 1.

Within the execution for `Yellow` Taxi data for the year `2020` and month `12`: what is the uncompressed file size (i.e. the output file `yellow_tripdata_2020-12.csv` of the `extract` task)?
- 128.3 MB
- 134.5 MB
- 364.7 MB
- 692.6 MB

### Solution 1:

We can add `disabled: true` to the `purge_files` task definition in the `02_postgres_taxi` flow.

```yaml
  - id: purge_files
    type: io.kestra.plugin.core.storage.PurgeCurrentExecutionFiles
    description: To avoid cluttering your storage, we will remove the downloaded files
    disabled: true
```

Execute it for December 2020 and check in the Outputs: extract -> outputFiles -> yellow_tripdata_2020-12.csv.

### Answer 1:

128.3 MB


## Question 2.

What is the rendered value of the variable `file` when the inputs `taxi` is set to `green`, `year` is set to `2020`, and `month` is set to `04` during execution?
- `{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv` 
- `green_tripdata_2020-04.csv`
- `green_tripdata_04_2020.csv`
- `green_tripdata_2020.csv`

### Solution 2:

Filename is rendered from input variables:

```
file: "{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv"
```

### Answer 2:

`green_tripdata_2020-04.csv`

## Question 3.

How many rows are there for the `Yellow` Taxi data for all CSV files in the year 2020?
- 13,537.299
- 24,648,499
- 18,324,219
- 29,430,127

### Solution 3:

Run backfill for the yellow taxi data for 2020 and query the 'yellow_tripdata' table in pgAdmin:

```sql
select
    count(*)
from
    public.yellow_tripdata
where
    filename like 'yellow_tripdata_2020-%'
```

### Answer 3:

24648499

## Question 4.

How many rows are there for the `Green` Taxi data for all CSV files in the year 2020?
- 5,327,301
- 936,199
- 1,734,051
- 1,342,034

### Solution 4:

Run backfill for the green taxi data for 2020 and query the 'green_tripdata' table:

```sql
select
    count(*)
from
    public.green_tripdata
where
    filename like 'green_tripdata_2020-%'
```

### Answer 4:

1734051

## Question 5.

How many rows are there for the `Yellow` Taxi data for the March 2021 CSV file?
- 1,428,092
- 706,911
- 1,925,152
- 2,561,031

### Solution 5:

Run backfill for the yellow taxi data for 2021 and query the 'yellow_tripdata' table in pgAdmin:

```sql
select
    count(*)
from
    public.yellow_tripdata
where
    filename like 'yellow_tripdata_2021-03%'
```

### Answer 5:

1925152

## Question 6.

How would you configure the timezone to New York in a Schedule trigger?
- Add a `timezone` property set to `EST` in the `Schedule` trigger configuration  
- Add a `timezone` property set to `America/New_York` in the `Schedule` trigger configuration
- Add a `timezone` property set to `UTC-5` in the `Schedule` trigger configuration
- Add a `location` property set to `New_York` in the `Schedule` trigger configuration  

### Solution 6:

Accordint to the [documentation](https://kestra.io/docs/workflow-components/triggers/schedule-trigger), `timezone` property can be specified in the `Schedule` trigger configuration.

When adding `timezone` in the editor, a help popup appears:


> The [\[time zone identifier\]](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) (i.e. the second column in [\[the Wikipedia table\]](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List) to use for evaluating the cron expression.\
Default value is the server default zone ID.\
Default value is : Etc/UTC


### Answer 6:

America/New_York
