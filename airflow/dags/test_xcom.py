from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def send_name(ti):
    ti.xcom_push(key ='name', value = 'james')

def say_hello(ti):
    name = ti.xcom_pull(task_ids = 'send_name', key = 'name')
    print("hello", name)

with DAG(
    dag_id = 'test_xcom',
    start_date = datetime(2024,4,30),
    schedule_interval = None
) as dag:
    task1 = PythonOperator(
        task_id = 'send_name',
        python_callable=send_name
    )

    task2 = PythonOperator(
        task_id = 'say_hello',
        python_callable=say_hello
    )


    task1 >> task2