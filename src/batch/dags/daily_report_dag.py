import pendulum
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.email import EmailOperator
from dags.scripts.generate_pdf_report import generate_pdf
from dags.scripts.move_json_files import move_json_files

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
            'input_dir': '/opt/airflow/output/daily_reports',
            'output_dir': '/opt/airflow/output/daily_reports'
        }
    )
    
    # 파일을 HDFS로 이동하는 작업 
    move_files_to_hdfs = PythonOperator(
        task_id='move_json_files',
        python_callable=move_json_files,
        provide_context=True
    )
    
    send_email_report = EmailOperator(
        task_id='send_email_report',
        to='wndus51445@gmail.com',
        subject='[뉴스 데이터] {{ ds }} 일일 뉴스 리포트',
        html_content="""
        <h3>{{ ds }} 일일 뉴스 리포트가 생성되었습니다.</h3>
        <p>첨부된 PDF 파일에서 상세 내용을 확인해주세요.</p>
        <p>감사합니다.</p>
        """,
        files=['/opt/airflow/output/daily_reports/{{ ds }}_report.pdf'],
        mime_subtype='mixed'
    )

    # 태스크 의존성 설정: Spark 작업 -> PDF 생성 -> 파일 이동 -> 이메일 전송
    submit_spark_job >> make_pdf_reports >> move_files_to_hdfs >> send_email_report