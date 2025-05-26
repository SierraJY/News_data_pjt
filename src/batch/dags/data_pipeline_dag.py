from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import pendulum

with DAG(
    dag_id='kafka_flink_data_ingestion',
    start_date=pendulum.datetime(2023, 1, 1, tz="Asia/Seoul"),
    schedule_interval='@daily', # 매일 실행하거나 필요에 따라 조정
    catchup=False,
    tags=['news', 'data_pipeline', 'realtime'],
    doc_md="""
    ### Kafka Flink Data Ingestion DAG
    This DAG orchestrates the data ingestion pipeline using Kafka Producer and Flink Consumer
    by executing commands inside the existing Docker containers.
    """,
) as dag:
    # 1. Kafka Producer 실행 태스크
    # docker exec 명령을 사용하여 kafka 컨테이너 내에서 news_producer.py 스크립트 실행
    # -it 옵션은 BashOperator에서는 불필요하거나 문제를 일으킬 수 있으므로 제거합니다.
    # BashOperator는 non-interactive 쉘을 사용합니다.
    run_kafka_producer_task = BashOperator(
        task_id='run_kafka_producer',
        bash_command='docker exec kafka python /opt/workspace/kafka_producer/news_producer.py',
        do_xcom_push=False, # 필요에 따라 XCom push 설정
        dag=dag,
    )

    # 2. Flink Consumer 실행 태스크
    # docker exec 명령을 사용하여 flink 컨테이너 내에서 flink_consumer.py 스크립트 실행
    run_flink_consumer_task = BashOperator(
        task_id='run_flink_consumer',
        bash_command='docker exec flink python /opt/workspace/flink_consumer/flink_consumer.py',
        do_xcom_push=False,
        dag=dag,
    )

    # 태스크 의존성 설정
    # Kafka Producer가 먼저 실행되고 완료된 후 Flink Consumer가 실행되도록 합니다.
    run_kafka_producer_task >> run_flink_consumer_task