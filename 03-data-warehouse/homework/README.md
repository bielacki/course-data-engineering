# Module 1 homework: Data warehouse

2025 cohort questions: [LINK](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2025/03-data-warehouse/homework.md)

## Data preparation

I used `wget` to download the Yellow Taxi Trip Records for January 2024 - June 2024.

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-{01..06}.parquet
```

Then I created the `data-engineering-zoomcamp-module03-homework` bucket in GCP.

And uploaded `.parquet` files using `gcloud` CLI:

```bash
gcloud storage cp *.parquet gs://data-engineering-zoomcamp-module03-homework
```

## BigQuery setup

Then I created an external table in BigQuery using GCP files:

```sql
create or replace external table
  `course-data-engineering.de_zoomcamp.external_yellow_tripdata`
options (
  format = 'parquet',
  uris = ['gs://data-engineering-zoomcamp-module03-homework/yellow_tripdata_2024-*.parquet']
)
```

Create a materialized table from the external table:

```sql
create or replace table
  `course-data-engineering.de_zoomcamp.materialized_yellow_tripdata` as (
    select * from `course-data-engineering.de_zoomcamp.external_yellow_tripdata`
  )
```

## Question 1.

What is count of records for the 2024 Yellow Taxi Data?
- 65,623
- 840,402
- 20,332,093
- 85,431,289

### Solution 1:

```sql
select
  count(*)
from
  `course-data-engineering.de_zoomcamp.materialized_yellow_tripdata`
```

Output:
```
20332093
```

### Answer 1:

- 20,332,093

## Question 2.

Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.</br> 
What is the **estimated amount** of data that will be read when this query is executed on the External Table and the Table?

- 18.82 MB for the External Table and 47.60 MB for the Materialized Table
- 0 MB for the External Table and 155.12 MB for the Materialized Table
- 2.14 GB for the External Table and 0MB for the Materialized Table
- 0 MB for the External Table and 0MB for the Materialized Table

### Solution 2:

**External table:**

```sql
select
  count(distinct PULocationID)
from
  `course-data-engineering.de_zoomcamp.external_yellow_tripdata`
```

Output:
```
This query will process 0 B when run.
```

**Materialized table:**

```sql
select
  count(distinct PULocationID)
from
  `course-data-engineering.de_zoomcamp.materialized_yellow_tripdata`
```

Output:
```
This query will process 155.12 MB when run.
```

### Answer 2:

- 0 MB for the External Table and 155.12 MB for the Materialized Table

## Question 3.

Write a query to retrieve the PULocationID from the table (not the external table) in BigQuery. Now write a query to retrieve the PULocationID and DOLocationID on the same table. Why are the estimated number of Bytes different?
- BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires 
reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.
- BigQuery duplicates data across multiple storage partitions, so selecting two columns instead of one requires scanning the table twice, 
doubling the estimated bytes processed.
- BigQuery automatically caches the first queried column, so adding a second column increases processing time but does not affect the estimated bytes scanned.
- When selecting multiple columns, BigQuery performs an implicit join operation between them, increasing the estimated bytes processed

### Solution 3:

```sql
select
  PULocationID
from
  `course-data-engineering.de_zoomcamp.materialized_yellow_tripdata`
```

Output:
```
This query will process 155.12 MB when run.
```

```sql
select
  PULocationID,
  DOLocationID
from
  `course-data-engineering.de_zoomcamp.materialized_yellow_tripdata`
```

Output:
```
This query will process 310.24 MB when run.
```

BigQuery is a columnar storage, in the second query we need to retrieve two columns and process more data.

### Answer 3:

- BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires 
reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.

## Question 4.

How many records have a fare_amount of 0?
- 128,210
- 546,578
- 20,188,016
- 8,333

### Solution 4:

```sql
select
  count(*) as zero_fare_amount
from
  `course-data-engineering.de_zoomcamp.materialized_yellow_tripdata`
where fare_amount = 0
```

Output:
```
8333
```

### Answer 4:

- 8,333

## Question 5.

What is the best strategy to make an optimized table in Big Query if your query will always filter based on tpep_dropoff_datetime and order the results by VendorID (Create a new table with this strategy)
- Partition by tpep_dropoff_datetime and Cluster on VendorID
- Cluster on by tpep_dropoff_datetime and Cluster on VendorID
- Cluster on tpep_dropoff_datetime Partition by VendorID
- Partition by tpep_dropoff_datetime and Partition by VendorID

### Solution 5:

```sql
create or replace table
  `course-data-engineering.de_zoomcamp.partitioned_clustered_yellow_tripdata`
partition by
  date(tpep_dropoff_datetime)
cluster by
  VendorID
as (
  select * from `course-data-engineering.de_zoomcamp.materialized_yellow_tripdata`
)
```

### Answer 5:

- Partition by tpep_dropoff_datetime and Cluster on VendorID

## Question 6.

Write a query to retrieve the distinct VendorIDs between tpep_dropoff_datetime
2024-03-01 and 2024-03-15 (inclusive)</br>

Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 5 and note the estimated bytes processed. What are these values? </br>

Choose the answer which most closely matches.</br> 

- 12.47 MB for non-partitioned table and 326.42 MB for the partitioned table
- 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table
- 5.87 MB for non-partitioned table and 0 MB for the partitioned table
- 310.31 MB for non-partitioned table and 285.64 MB for the partitioned table

### Solution 6:

**For materialized table:**

```sql
select
  count(distinct VendorID)
from
  `course-data-engineering.de_zoomcamp.materialized_yellow_tripdata`
where
  date(tpep_dropoff_datetime) between '2024-03-01' and '2024-03-15'
```

Output:
```
This query will process 310.24 MB when run.
```

For partitioned and clustered table:

```sql
select
  count(distinct VendorID)
from
  `course-data-engineering.de_zoomcamp.partitioned_clustered_yellow_tripdata`
where
  date(tpep_dropoff_datetime) between '2024-03-01' and '2024-03-15'
```

Output:
```
This query will process 26.84 MB when run.
```

### Answer 6:

- 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table

## Question 7.

Where is the data stored in the External Table you created?

- Big Query
- Container Registry
- GCP Bucket
- Big Table

### Solution 7:

- GCP Bucket

### Answer 7:

- GCP Bucket

## Question 8.

It is best practice in Big Query to always cluster your data:
- True
- False

### Solution 8:

> Clustering smaller tables or partitions is possible, but the performance improvement is usually negligible.

### Answer 8:

- False

## (Bonus: Not worth points) Question 9:
No Points: Write a `SELECT count(*)` query FROM the materialized table you created. How many bytes does it estimate will be read? Why?

```sql
select
  count(*)
from
  `course-data-engineering.de_zoomcamp.materialized_yellow_tripdata`
```

Output:
```
This query will process 0 B when run.
```

BigQuery already has the information about row count in table metadata, so it doesn't have to actually query data.