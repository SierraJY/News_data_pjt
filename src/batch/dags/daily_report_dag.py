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
    dag_id='daily_report_dag_hdfs',
    default_args=default_args,
    description='매일 새벽 1시에 Spark를 이용해 HDFS 데이터로 뉴스 리포트 생성',
    schedule_interval='0 1 * * *',
    start_date=datetime(2025, 5, 1, tzinfo=local_tz),
    catchup=False,
    tags=['daily', 'report', 'spark', 'hdfs']
) as dag:
    
    # HDFS 상태 확인 태스크
    check_hdfs_status = BashOperator(
        task_id='check_hdfs_status',
        bash_command='''
        echo "HDFS 상태 확인 중..."
        curl -s "http://namenode:9870/jmx?qry=Hadoop:service=NameNode,name=NameNodeStatus" | head -n 5 || echo "HDFS 상태 확인 실패"
        echo "HDFS realtime 디렉토리 확인:"
        curl -s "http://namenode:9870/webhdfs/v1/user/realtime/?op=LISTSTATUS" | grep -o '"pathSuffix":"[^"]*"' | wc -l || echo "realtime 디렉토리 확인 실패"
        echo "HDFS news_archive 디렉토리 확인:"
        curl -s "http://namenode:9870/webhdfs/v1/user/news_archive/?op=LISTSTATUS" | grep -o '"pathSuffix":"[^"]*"' | wc -l || echo "news_archive 디렉토리 확인 실패"
        '''
    )
    
    # Spark 작업으로 HDFS에서 데이터 읽어서 리포트 생성
    submit_spark_job = SparkSubmitOperator(
        task_id='spark_daily_report_hdfs',
        application='/opt/airflow/dags/scripts/spark_daily_report.py',
        conn_id='spark_default',
        application_args=['--date', '{{ ds }}'],
        conf={
            'spark.master': 'spark://spark-master:7077',
            'spark.sql.adaptive.enabled': 'true',
            'spark.sql.adaptive.coalescePartitions.enabled': 'true'
        }
    )

    # PDF 리포트 생성
    make_pdf_reports = PythonOperator(
        task_id='make_pdf_reports',
        python_callable=generate_pdf,
        op_kwargs={
            'date': '{{ ds }}',
            'input_dir': '/opt/airflow/output/daily_reports',
            'output_dir': '/opt/airflow/output/daily_reports'
        }
    )
    
    # HDFS 내에서 파일 이동 (realtime → news_archive)
    move_files_to_archive = PythonOperator(
        task_id='move_json_files_hdfs',
        python_callable=move_json_files,
        provide_context=True
    )
    
    # 이메일 리포트 전송
    send_email_report = EmailOperator(
        task_id='send_email_report',
        to=['wndus51445@gmail.com','yeeunyoo99@naver.com'],
        subject='[뉴스 데이터 HDFS] {{ ds }} 일일 뉴스 리포트',
        html_content="""
        <h3>{{ ds }} 일일 뉴스 리포트가 생성되었습니다.</h3>
        <p><strong>데이터 소스:</strong> HDFS (/user/realtime/)</p>
        <p><strong>아카이브:</strong> HDFS (/user/news_archive/{{ ds | replace("-", "/") }}/)</p>
        <p><strong>처리 방식:</strong> Flink → HDFS → Spark → PDF → Archive</p>
        <p>첨부된 PDF 파일에서 상세 내용을 확인해주세요.</p>
        <p>감사합니다.</p>
        """,
        files=['/opt/airflow/output/daily_reports/{{ ds }}_report.pdf'],
        mime_subtype='mixed'
    )

    # 태스크 의존성 설정: HDFS 확인 → Spark 작업 → PDF 생성 → 파일 아카이브 → 이메일 전송
    check_hdfs_status >> submit_spark_job >> make_pdf_reports >> move_files_to_archive >> send_email_report