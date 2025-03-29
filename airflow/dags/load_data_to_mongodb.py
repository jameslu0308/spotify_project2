from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.mongo.hooks.mongo import MongoHook

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 29, 4, 5),
    'retries': 1,
}

def load_data_to_mongodb():
    # MongoDB connection details
    mongo_db = 'Spotify'
    mongo_collection = 'test_collection'

    # Create MongoHook
    hook = MongoHook(mongo_conn_id='my_mongo_conn')

    # Connect to MongoDB
    client = hook.get_conn()

    # Access database and collection
    db = client[mongo_db]
    collection = db[mongo_collection]

    try:
        # Define time data to insert
        time_data = {'timestamp': datetime.now()}

        # Insert data into MongoDB
        collection.insert_one(time_data)
        print("Data inserted successfully into MongoDB.")
    finally:
        # Close MongoDB connection
        client.close()

dag = DAG(
    dag_id = 'load_data_to_mongodb',
    default_args=default_args,
    schedule_interval='*/5 * * * *',  # Run every 5 minutes
    catchup=False,
)

task_load_data_to_mongodb = PythonOperator(
    task_id='load_data_to_mongodb',
    python_callable=load_data_to_mongodb,
    dag=dag,
)

task_load_data_to_mongodb
