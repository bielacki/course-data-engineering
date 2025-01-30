# Module 1 homework: Docker, SQL and Terraform

2025 cohort questions: [LINK](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2025/01-docker-terraform/homework.md)

## Question 1. Understanding docker first run

Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`.

What's the version of `pip` in the image?

- 24.3.1
- 24.2.1
- 23.3.1
- 23.2.1

### Solution 1:

```bash
docker container run -it --entrypoint=bash python:3.12.8
```

Output:
```bash
# Unable to find image 'python:3.12.8' locally
# 3.12.8: Pulling from library/python
# e474a4a4cbbf: Already exists 
# d22b85d68f8a: Already exists 
# 936252136b92: Already exists 
# 94c5996c7a64: Already exists 
# c980de82d033: Already exists 
# c80762877ac5: Pull complete 
# 86f9cc2995ad: Pull complete 
# Digest: sha256:2e726959b8df5cd9fd95a4cbd6dcd23d8a89e750e9c2c5dc077ba56365c6a925
# Status: Downloaded newer image for python:3.12.8
```

```bash
pip --version
```

Output:
```bash
# pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```
### Answer 1:

24.3.1

## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that **pgadmin** should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin  

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```

- postgres:5433
- localhost:5432
- db:5433
- postgres:5432
- db:5432

If there are more than one answers, select only one of them

### Solution 2:

We should look for a service name and container destination port. Since the `pgadmin` service will be connecting to the `db` service , we should put `db` as the `hostname` in the pgAdmin UI.

And ports for the `db` serveice mapped as '5433:5432', s othe destination port is `5432`.

So, in the `port` field in the pgAdmin UI we should specify `5432`.

! Answer `postgres:5432` is also correct, because container_name is also can be used to specify hostname in pgAdmin.

### Answer 2:

db:5432

##  Prepare Postgres

Run Postgres and load data as shown in the videos
We'll use the green taxi trips from October 2019:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz
```

You will also need the dataset with zones:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

Download this data and put it into Postgres.

You can use the code from the course. It's up to you whether
you want to use Jupyter or a python script.

## Question 3. Trip Segmentation Count

During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, **respectively**, happened:
1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles 

Answers:

- 104,802;  197,670;  110,612;  27,831;  35,281
- 104,802;  198,924;  109,603;  27,678;  35,189
- 104,793;  201,407;  110,612;  27,831;  35,281
- 104,793;  202,661;  109,603;  27,678;  35,189
- 104,838;  199,013;  109,645;  27,688;  35,202

### Solution 3:

Verify, how many rows the CSV file has:

```bash
wc -l green_tripdata_2019-10.csv
```
Output:
```bash
# 476387 green_tripdata_2019-10.csv
```

Ingest Green taxi data into Postgres and check how many rows ingested the `green_taxi_data` table has:

```sql
SELECT count(*) FROM public.green_taxi_data
```
Query result:\
476386

Now let's query our table:

```sql
select
	case
		when trip_distance <= 1 then '< 1'
		when trip_distance > 1 and trip_distance <= 3 then '1-3'
		when trip_distance > 3 and trip_distance <= 7 then '3-7'
		when trip_distance > 7 and trip_distance <= 10 then '7-10'
		when trip_distance > 10 then '10+'
	end as trip_distance,
	count(*) as trips
from
	public.green_taxi_data
where 
	date(lpep_pickup_datetime) >= '2019.10.01' and date(lpep_dropoff_datetime) < '2019.11.01'
group by 1
```

Result:

| trip_distance    | trips |
| -------- | ------- |
| "< 1" | 104802 |
| "1-3"	| 198924 |
| "3-7"	| 109603 |
| "7-10" | 27678 |
| "10+" | 35189 |

### Answer 3:

104,802; 198,924; 109,603; 27,678; 35,189

## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance?
Use the pick up time for your calculations.

Tip: For every day, we only care about one single trip with the longest distance. 

- 2019-10-11
- 2019-10-24
- 2019-10-26
- 2019-10-31

### Solution 4:

Query:

```sql
select
	date(lpep_pickup_datetime),
	max(trip_distance) as max_trip_distance
from
	public.green_taxi_data
group by 1
order by 2 desc
limit 1
```
Result:

| date  | max_trip_distance |
| -------- | ------- |
| 2019-10-31 | 515.89 |

### Answer 4:

2019-10-31

## Question 5. Three biggest pickup zones

Which were the top pickup locations with over 13,000 in
`total_amount` (across all trips) for 2019-10-18?

Consider only `lpep_pickup_datetime` when filtering by date.
 
- East Harlem North, East Harlem South, Morningside Heights
- East Harlem North, Morningside Heights
- Morningside Heights, Astoria Park, East Harlem South
- Bedford, East Harlem North, Astoria Park

### Solution 5:

Query:

```sql
with trips_data as (
	select
		"PULocationID" as pickup_location_id,
		sum(total_amount) as amount
	from
		public.green_taxi_data
	where date(lpep_pickup_datetime) = '2019-10-18'
	group by 1
)

select
	zone_lookup."Zone" as zone_name,
	trips_data.amount as total_amount
from
	trips_data
	left join public.taxi_zone_lookup as zone_lookup on trips_data.pickup_location_id = zone_lookup."LocationID"
where
	trips_data.amount > 13000
```

Result:
| zone_name  | total_amount |
| -------- | ------- |
| East Harlem North | 18686.680000000088 |
| East Harlem South | 16797.26000000006 |
| Morningside Heights | 13029.79000000004 |


### Answer 5:

East Harlem North, East Harlem South, Morningside Heights

## Question 6. Largest tip

For the passengers picked up in October 2019 in the zone
named "East Harlem North" which was the drop off zone that had
the largest tip?

Note: it's `tip` , not `trip`

We need the name of the zone, not the ID.

- Yorkville West
- JFK Airport
- East Harlem North
- East Harlem South

### Solution 6:

Query:
```sql
with prep as (
	select
		trips_data."PULocationID" as pickup_location_id,
		zone_lookup_pu."Zone" as pickup_zone_name,
		trips_data."DOLocationID" as dropoff_location_id,
		zone_lookup_do."Zone" as dropoff_zone_name,
		tip_amount
	from
		public.green_taxi_data as trips_data
		left join public.taxi_zone_lookup as zone_lookup_pu on trips_data."PULocationID" = zone_lookup_pu."LocationID"
		left join public.taxi_zone_lookup as zone_lookup_do on trips_data."DOLocationID" = zone_lookup_do."LocationID"
	where
		date(lpep_pickup_datetime) >= '2019-10-01' and date(lpep_pickup_datetime) < '2019-11-01'
	order by trips_data.tip_amount desc
)

select
	dropoff_zone_name,
	tip_amount
from prep
where pickup_zone_name = 'East Harlem North'
limit 1
```

Result:
| dropoff_zone_name  | tip_amount |
| -------- | ------- |
| JFK Airport | 87.3 |

### Answer 6:

JFK Airport

## Terraform

In this section homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP/Laptop/GitHub Codespace install Terraform. 
Copy the files from the course repo
[here](../../../01-docker-terraform/1_terraform_gcp/terraform) to your VM/Laptop/GitHub Codespace.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.


## Question 7. Terraform Workflow

Which of the following sequences, **respectively**, describes the workflow for: 
1. Downloading the provider plugins and setting up backend,
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform`

Answers:
- terraform import, terraform apply -y, terraform destroy
- teraform init, terraform plan -auto-apply, terraform rm
- terraform init, terraform run -auto-approve, terraform destroy
- terraform init, terraform apply -auto-approve, terraform destroy
- terraform import, terraform apply -y, terraform rm

### Solution 7:

> 1. Downloading the provider plugins and setting up backend

terraform init

> 2. Generating proposed changes and auto-executing the plan

terraform apply -auto-approve

> 3. Remove all resources managed by terraform

terraform destroy

### Answer 7:

terraform init, terraform apply -auto-approve, terraform destroy

## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2025/homework/hw1