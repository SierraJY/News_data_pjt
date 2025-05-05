from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def hello_world_function():
    print("Hello World!")
    return "Hello World!"

with DAG(
    'test_hello_world',
    default_args=default_args,
    description='A simple hello world DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:
    
    hello_world_task = PythonOperator(
        task_id='hello_world_task',
        python_callable=hello_world_function,
    )

    hello_world_task 