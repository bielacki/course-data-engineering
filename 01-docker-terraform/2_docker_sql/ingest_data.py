import pandas as pd
import argparse
import os
from sqlalchemy import create_engine
from time import time

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    database = params.database
    table = params.table
    # url = params.url

    # file_name = "output.parquet"

    # os.system(f"wget {url} -O {file_name}")

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")

    df = pd.read_csv("source_data/taxi_zone_lookup.csv", nrows=100)

    # df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    # df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    df.head(n=0).to_sql(name="taxi_zone_lookup", con=engine, if_exists="replace")

    df_iter = pd.read_csv("source_data/taxi_zone_lookup.csv", iterator=True, chunksize=100000)

    while True:
        t_start = time()

        # Get dataframes fromCSV one by one. Each time we call next() function, it returns
        # the next chunk from the df_iter iterator, incremented by chunksize

        df = next(df_iter)

        # Since tpep_pickup_datetime and tpep_dropoff_datetime are of a TEXT type,
        # we convert them to datetime using to_datetime Pandas function

        # df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        # df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

        # Then we want to upload dataframes from iterator one by one.
        # In this case we don't want to replace the table, but to append new chunks.

        df.to_sql(name=table, con=engine, if_exists="append")

        t_end = time()

        print(f"Inserted another chunk, took {round(t_end - t_start, 3)} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--database', help='database name for postgres')
    parser.add_argument('--table', help='table name for postgres')
    # parser.add_argument('--url', help='url of the csv file')

    args = parser.parse_args()

    main(args)