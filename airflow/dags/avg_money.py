import json
from datetime import datetime
from airflow import DAG
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator
def extract(ti):
    js_string = """
                [
                    {
                        "order_id": "1001",
                        "order_item": "薯餅蛋餅",
                        "order_price": 45
                    },
                    {
                        "order_id": "1002",
                        "order_item": "大冰奶",
                        "order_price": 35
                    }
                ]
                 """
    order_data = json.loads(js_string)
    ti.xcom_push(key = 'order_data', value = order_data)

def transform_sum(ti):
    order_data_list = ti.xcom_pull(task_ids = 'extract', key = 'order_data')
    order_total = 0
    for order_dict in order_data_list:
        order_total +=order_dict['order_price']
    ti.xcom_push(key = 'order_total', value = order_total)

def transform_count(ti):
    order_data_list = ti.xcom_pull(task_ids = 'extract', key = 'order_data')
    order_count = len(order_data_list)
    ti.xcom_push(key = 'order_count', value = order_count)

def transform_average(ti):
    order_total = ti.xcom_pull(
        task_ids = 'transform.transform_sum', key = 'order_total'
    )
    order_count = ti.xcom_pull(
        task_ids = 'transform.transform_count', key = 'order_count'
    )
    order_average = order_total/order_count
    ti.xcom_push(key = 'order_average', value = order_average)

def load(ti):
    # 因此，'transform.transform_average' 表示您想要从 transform TaskGroup 中的 transform_average 任务获取 XCom 值。
    order_average = ti.xcom_pull(
        task_ids = 'transform.transform_average', key = 'order_average'
    )
    print(f'Average Order Price: {order_average}')

with DAG(
    dag_id = 'avg_money',
    schedule_interval = None,
    start_date = datetime(2024,5,2)
)as dag:
    extract = PythonOperator(
        task_id = 'extract',
        python_callable = extract
    )
    with TaskGroup(group_id = 'transform') as transform:
        transform_sum = PythonOperator(
            task_id = 'transform_sum',
            python_callable = transform_sum
        )        
        transform_count = PythonOperator(
            task_id = 'transform_count',
            python_callable = transform_count
        )
        transform_average = PythonOperator(
            task_id = 'transform_average',
            python_callable = transform_average
        )
        [transform_sum, transform_count] >> transform_average

    load = PythonOperator(
        task_id = 'load',
        python_callable=load
    )
    extract >> transform >> load

    
