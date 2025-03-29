import json
from airflow.decorators import dag, task, task_group
from datetime import datetime
from airflow.operators.empty import EmptyOperator
@dag(schedule = None, start_date = datetime(2024,5,2))
def taskflow_etl_dag():
    @task()
    def extract():
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
        return order_data
    @task_group
    def transform(order_data):
        @task()
        def transform_sum(order_data_json):
            order_total = 0
            for order_dict in order_data_json:
                order_total +=order_dict['order_price']
                return order_total
            
        @task()
        def transform_count(order_data_json):
            order_count = len(order_data_json)
            return order_count
        
        @task()
        def transform_average(order_total, order_count):
            order_average = order_total/order_count
            return order_average
        
        order_average_result = transform_average(
            transform_sum(order_data), transform_count(order_data)
        )
        return order_average_result
    

    task_3 = EmptyOperator(task_id = 'task_3')

    @task()
    def load(order_average):
        print(f"Average Order Price: {order_average}")

    task_3 >> load(transform(extract())) 


taskflow_etl_dag()
    

    

    
