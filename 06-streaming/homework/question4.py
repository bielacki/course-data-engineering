import csv
import json
from kafka import KafkaProducer
from time import time

def main():
    t0 = time()

    # Create a Kafka producer
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    csv_file = 'data/green_tripdata_2019-10.csv'  # change to your CSV file path if needed

    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        filter_columns = ['lpep_pickup_datetime',\
            'lpep_dropoff_datetime',\
            'PULocationID',\
            'DOLocationID',\
            'passenger_count',\
            'trip_distance',\
            'tip_amount']

        for row in reader:
            filtered_row = {key: row[key] for key in filter_columns if key in row}
            # Each row will be a dictionary keyed by the CSV headers
            # Send data to Kafka topic "green-trips"
            # producer.send('green-trips', value=filtered_row)
            producer.send('green-trips', value=row)

    # Make sure any remaining messages are delivered
    producer.flush()
    producer.close()

    t1 = time()
    took = t1 - t0
    print(took)


if __name__ == "__main__":
    main()