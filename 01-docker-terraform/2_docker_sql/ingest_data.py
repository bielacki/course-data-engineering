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
    url = params.url

    file_name = "output.parquet"

    os.system(f"wget {url} -O {file_name}")

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")

    df = pd.read_parquet(file_name)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    t_start = time()

    df.to_sql(name=table, con=engine, if_exists="replace")

    t_end = time()
    
    print(f"Inserted data, took {round(t_end - t_start, 3)} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--database', help='database name for postgres')
    parser.add_argument('--table', help='table name for postgres')
    parser.add_argument('--url', help='url of the data file')

    args = parser.parse_args()

    main(args)