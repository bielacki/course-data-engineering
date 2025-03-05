# Module 5 Homework: Batch

[Homework notebook](/homework.ipynb).

In this homework we'll put what we learned about Spark in practice.

For this homework we will be using the Yellow 2024-10 data from the official website: 

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-10.parquet
```


## Question 1: Install Spark and PySpark

- Install Spark
- Run PySpark
- Create a local spark session
- Execute spark.version.

What's the output?

> [!NOTE]
> To install PySpark follow this [guide](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/05-batch/setup/pyspark.md)

### Solution 1:

```bash
uv python pin 3.10 
uv init --bare 
uv add pyspark
source .venv/bin/activate
pyspark
```

Output:

```
Python 3.10.15 (main, Oct 16 2024, 08:33:15) [Clang 18.1.8 ] on darwin
Type "help", "copyright", "credits" or "license" for more information.
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
25/03/05 20:48:23 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /__ / .__/\_,_/_/ /_/\_\   version 3.5.5
      /_/

Using Python version 3.10.15 (main, Oct 16 2024 08:33:15)
Spark context Web UI available at http://192.168.0.45:4040
Spark context available as 'sc' (master = local[*], app id = local-1741204103643).
SparkSession available as 'spark'.
```

```bash
spark.version
```

Output:

```
'3.5.5'
```

### Answer 1:

'3.5.5'

## Question 2: Yellow October 2024

Read the October 2024 Yellow into a Spark Dataframe.

Repartition the Dataframe to 4 partitions and save it to parquet.

What is the average size of the Parquet (ending with .parquet extension) Files that were created (in MB)? Select the answer which most closely matches.

- 6MB
- 25MB
- 75MB
- 100MB

### Solution 2:


```python
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('homework5') \
    .getOrCreate()

df = spark.read \
    .option("header", "true") \
    .parquet('yellow_tripdata_2024-10.parquet')

df.repartition(4).write.parquet('data/question2/', mode='overwrite')
```

```bash
cd data/question2/
ls -alh
```

Example from the output:
```
-rw-r--r--   1 m  staff    22M Mar  5 21:07 part-00000-cb650cf6-e1a5-4077-88f6-1cca756b4e01-c000.snappy.parquet
```

### Answer 2:

25MB

## Question 3: Count records 

How many taxi trips were there on the 15th of October?

Consider only trips that started on the 15th of October.

- 85,567
- 105,567
- 125,567
- 145,567

### Solution 3:

```python
df.createOrReplaceTempView('yellow_trips')

df_yellow_trips = spark.sql("""
SELECT 
    COUNT(*) AS number_of_trips
FROM
    yellow_trips
WHERE
    date(tpep_pickup_datetime) = '2024-10-15'
""")

df_yellow_trips.show()
```

Output:

```
+---------------+
|number_of_trips|
+---------------+
|         128893|
+---------------+
```


### Answer 3:

125,567 (closest answer)

## Question 4: Longest trip

What is the length of the longest trip in the dataset in hours?

- 122
- 142
- 162
- 182

### Solution 4:

```python
df_longest_trip = spark.sql("""
select
    max(timestampdiff(hour, tpep_pickup_datetime, tpep_dropoff_datetime)) as longest_trip_hours
from
    yellow_trips
""")

df_longest_trip.show()
```

Output:

```
+------------------+
|longest_trip_hours|
+------------------+
|               162|
+------------------+
```

### Answer 4:

162

## Question 5: User Interface

Spark’s User Interface which shows the application's dashboard runs on which local port?

- 80
- 443
- 4040
- 8080

### Solution 5:

http://localhost:4040/

### Answer 5:

4040

## Question 6: Least frequent pickup location zone

Load the zone lookup data into a temp view in Spark:

```bash
wget https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
```

Using the zone lookup data and the Yellow October 2024 data, what is the name of the LEAST frequent pickup location Zone?

- Governor's Island/Ellis Island/Liberty Island
- Arden Heights
- Rikers Island
- Jamaica Bay

### Solution 6:

```python
df_zone_lookup = spark.read \
    .option("header", "true") \
    .csv('taxi_zone_lookup.csv')

df_zone_lookup.createOrReplaceTempView('zone_lookup')

df_least_frequent_pickup_zone = spark.sql("""
with pickup_zones as (
    select
        PULocationID,
        count(*) as trips_count
    from yellow_trips
    group by 1
)

select
    pickup_zones.PULocationID,
    pickup_zones.trips_count,
    zone_lookup.Zone
from
    pickup_zones
    left join zone_lookup on pickup_zones.PULocationID = zone_lookup.LocationID
order by pickup_zones.trips_count asc
limit 1
"""
)

df_least_frequent_pickup_zone.show(truncate=False)
```

Output:

```
+------------+-----------+---------------------------------------------+
|PULocationID|trips_count|Zone                                         |
+------------+-----------+---------------------------------------------+
|105         |1          |Governor's Island/Ellis Island/Liberty Island|
+------------+-----------+---------------------------------------------+
```

### Answer 6:

Governor's Island/Ellis Island/Liberty Island
