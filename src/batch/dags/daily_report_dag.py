import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from dags.scripts.generate_pdf_report import generate_pdf

local_tz = pendulum.timezone("Asia/Seoul")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='daily_report_dag',
    default_args=default_args,
    description='매일 새벽 1시에 Spark를 이용해 뉴스 리포트 생성',
    schedule_interval='0 1 * * *',
    start_date=datetime(2025, 5, 1, tzinfo=local_tz),
    catchup=False,
    tags=['daily', 'report', 'spark']
) as dag:
    
    submit_spark_job = SparkSubmitOperator(
        task_id='spark_daily_report',
        application='/opt/airflow/dags/scripts/spark_daily_report.py',
        conn_id='spark_default',
        application_args=['--date', '{{ ds }}'],
        conf={'spark.master': 'spark://spark-master:7077'}
    )

    make_pdf_reports = PythonOperator(
        task_id='make_pdf_reports',
        python_callable=generate_pdf,
        op_kwargs={
            'date': '{{ ds }}',
            'input_dir': '/opt/airflow/data/news_archive',
            'output_dir': '/opt/airflow/data/daily_reports'
        }
    )

    submit_spark_job >> make_pdf_reports