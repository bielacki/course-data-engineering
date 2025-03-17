from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, DataTypes, TableEnvironment, StreamTableEnvironment
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.time import Duration

def create_green_events_aggregated_sink(t_env):
    table_name = 'processed_green_events_aggregated'
    sink_ddl = f"""
        CREATE OR REPLACE TABLE {table_name} (
            PULocationID INTEGER,
            DOLocationID INTEGER,
            longest_streak BIGINT,
            PRIMARY KEY (PULocationID, DOLocationID) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = '{table_name}',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        );
        """
    t_env.execute_sql(sink_ddl)
    return table_name

def create_events_source_kafka(t_env):
    table_name = "events"
    source_ddl = f"""
        CREATE TABLE {table_name} (
            lpep_pickup_datetime TIMESTAMP(3),
            lpep_dropoff_datetime TIMESTAMP(3),
            PULocationID INTEGER,
            DOLocationID INTEGER,
            passenger_count VARCHAR,
            trip_distance DOUBLE,
            tip_amount DOUBLE,
            dropoff_timestamp as lpep_dropoff_datetime,
            WATERMARK for dropoff_timestamp as dropoff_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = 'redpanda-1:29092',
            'topic' = 'green-trips',
            'scan.startup.mode' = 'earliest-offset',
            'properties.auto.offset.reset' = 'earliest',
            'format' = 'json'
        );
        """
    t_env.execute_sql(source_ddl)
    return table_name

def longest_streak():
    # Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10 * 1000)
    env.set_parallelism(1)

    # Set up the table environment
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    try:
        # Create Kafka table
        source_table = create_events_source_kafka(t_env)
        aggregated_table = create_green_events_aggregated_sink(t_env)

        t_env.execute_sql(f"""
        INSERT INTO {aggregated_table}
        SELECT
            PULocationID,
            DOLocationID,
            count(*) as longest_streak
        FROM {source_table}
        GROUP BY 
            PULocationID, 
            DOLocationID,
            SESSION(dropoff_timestamp, INTERVAL '5' MINUTE)
        """).wait()

    except Exception as e:
        print("Writing records from Kafka to JDBC failed:", str(e))


if __name__ == '__main__':
    longest_streak()
