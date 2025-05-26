import pendulum
import os
import re # 정규표현식 임포트
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.email import EmailOperator
from airflow.utils.task_group import TaskGroup
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
    dag_id='news_data_pipeline_unified',
    default_args=default_args,
    description='통합 뉴스 데이터 파이프라인: 실시간 수집 → 처리 → 분석 → 리포트 생성',
    schedule_interval='@daily',  # 매일 실행
    start_date=datetime(2025, 5, 1, tzinfo=local_tz),
    catchup=False,
    tags=['news', 'data_pipeline', 'realtime', 'hdfs', 'spark', 'report'],
    doc_md="""
    ### 통합 뉴스 데이터 파이프라인 DAG

    이 DAG는 뉴스 데이터의 전체 생명주기를 관리합니다:

    **1. 실시간 데이터 수집 그룹:**
    - Kafka Producer: RSS 뉴스 수집 및 Kafka 전송 (발행 메시지 개수 XCom 전달)
    - Flink Consumer: Kafka → AI 처리 → PostgreSQL & HDFS 저장 (XCom 메시지 개수 기반 종료)

    **2. 배치 분석 및 리포팅 그룹:**
    - HDFS 상태 확인
    - Spark 배치 작업: HDFS 데이터 분석
    - PDF 리포트 생성
    - 파일 아카이브
    - 이메일 리포트 전송

    **데이터 흐름:**
    RSS → Kafka → Flink (AI 처리) → HDFS → Spark → PDF → Email
    """,
) as dag:

    # ========================================
    # 1. 실시간 데이터 수집 TaskGroup
    # ========================================
    with TaskGroup(
        group_id='realtime_data_ingestion',
        tooltip='실시간 뉴스 데이터 수집 및 처리'
    ) as realtime_group:

        # Kafka Producer 실행 태스크
        # 표준 출력에서 "Total messages produced: [N]" 패턴을 찾아 XCom으로 푸시
        run_kafka_producer_task = BashOperator(
            task_id='run_kafka_producer',
            bash_command='''
            python_output=$(docker exec kafka python /opt/workspace/kafka_producer/news_producer_with_XCOM.py 2>&1)
            echo "$python_output"
            # 마지막 라인에서 메시지 개수 추출
            MESSAGE_COUNT=$(echo "$python_output" | tail -n 10 | grep -oP 'Total messages produced: \K\d+' | tail -1)
            echo "Extracted MESSAGE_COUNT: $MESSAGE_COUNT"
            # Airflow XCom으로 푸시 (task_id는 run_kafka_producer_task)
            echo "$MESSAGE_COUNT"
            ''',
            do_xcom_push=True, # 표준 출력의 마지막 라인을 XCom으로 푸시
            doc_md="""
            ### Kafka Producer
            - RSS 피드에서 뉴스 데이터 수집
            - 크롤링을 통한 본문 내용 추출
            - Kafka 토픽 'news'로 데이터 전송
            - **전송된 메시지 개수를 XCom으로 전달**
            """
        )

        # Flink Consumer 실행 태스크
        # Kafka Producer에서 XCom으로 받은 메시지 개수를 Flink Consumer에 인자로 전달
        run_flink_consumer_task = BashOperator(
            task_id='run_flink_consumer',
            bash_command='''
            MESSAGES_TO_PROCESS="{{ task_instance.xcom_pull(task_ids='realtime_data_ingestion.run_kafka_producer', key='return_value') }}"
            echo "Flink Consumer가 처리할 메시지 개수: $MESSAGES_TO_PROCESS"
            # Flink 컨슈머 스크립트에 메시지 개수를 인자로 전달
            docker exec flink python /opt/workspace/flink_consumer/flink_consumer_with_XCOM.py "$MESSAGES_TO_PROCESS"
            ''',
            do_xcom_push=False,
            doc_md="""
            ### Flink Consumer
            - Kafka에서 뉴스 데이터 소비
            - AI 기반 전처리 (카테고리 분류, 키워드 추출, 임베딩)
            - PostgreSQL 및 HDFS 동시 저장
            - **Kafka Producer가 전달한 메시지 개수만큼 처리 후 자동 종료**
            """
        )

        # 실시간 그룹 내 의존성
        run_kafka_producer_task >> run_flink_consumer_task

    # ========================================
    # 2. 배치 분석 및 리포팅 TaskGroup
    # ========================================
    with TaskGroup(
        group_id='batch_analysis_reporting',
        tooltip='배치 분석 및 일일 리포트 생성'
    ) as batch_group:

        # HDFS 상태 확인 태스크
        check_hdfs_status = BashOperator(
            task_id='check_hdfs_status',
            bash_command='''
            echo "📊 HDFS 상태 확인 중..."
            echo "=== NameNode 상태 ==="
            curl -s "http://namenode:9870/jmx?qry=Hadoop:service=NameNode,name=NameNodeStatus" | head -n 5 || echo "⚠️ HDFS 상태 확인 실패"

            echo "=== Realtime 디렉토리 파일 수 ==="
            REALTIME_COUNT=$(curl -s "http://namenode:9870/webhdfs/v1/user/realtime/?op=LISTSTATUS" | grep -o '"pathSuffix":"[^"]*"' | wc -l || echo "0")
            echo "📁 /user/realtime/ 파일 수: $REALTIME_COUNT"

            echo "=== Archive 디렉토리 상태 ==="
            ARCHIVE_COUNT=$(curl -s "http://namenode:9870/webhdfs/v1/user/news_archive/?op=LISTSTATUS" | grep -o '"pathSuffix":"[^"]*"' | wc -l || echo "0")
            echo "📁 /user/news_archive/ 디렉토리 수: $ARCHIVE_COUNT"

            echo "✅ HDFS 상태 확인 완료"
            ''',
            doc_md="""
            ### HDFS 상태 확인
            - NameNode 헬스 체크
            - /user/realtime/ 디렉토리의 파일 수 확인
            - /user/news_archive/ 디렉토리 상태 확인
            """
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
                'spark.sql.adaptive.coalescePartitions.enabled': 'true',
                'spark.sql.catalog.spark_catalog.type': 'hadoop',
                'spark.hadoop.fs.defaultFS': 'hdfs://namenode:9000'
            },
            doc_md="""
            ### Spark 일일 분석 작업
            - HDFS /user/realtime/ 디렉토리에서 뉴스 데이터 읽기
            - 카테고리별, 소스별, 시간대별 분석
            - 키워드 트렌드 분석
            - 분석 결과를 /opt/airflow/output/daily_reports/에 저장
            """
        )

        # PDF 리포트 생성
        make_pdf_reports = PythonOperator(
            task_id='make_pdf_reports',
            python_callable=generate_pdf,
            op_kwargs={
                'date': '{{ ds }}',
                'input_dir': '/opt/airflow/output/daily_reports',
                'output_dir': '/opt/airflow/output/daily_reports'
            },
            doc_md="""
            ### PDF 리포트 생성
            - Spark 분석 결과를 PDF 형태로 변환
            - 차트 및 그래프 포함
            - 이메일 첨부용 최종 리포트 생성
            """
        )

        # HDFS 내에서 파일 이동 (realtime → news_archive)
        move_files_to_archive = PythonOperator(
            task_id='move_json_files_hdfs',
            python_callable=move_json_files,
            provide_context=True,
            doc_md="""
            ### 파일 아카이브
            - /user/realtime/ → /user/news_archive/{{ ds }}/로 파일 이동
            - 처리 완료된 뉴스 데이터 정리
            - HDFS 스토리지 효율성 향상
            """
        )

        # 이메일 리포트 전송
        send_email_report = EmailOperator(
            task_id='send_email_report',
            to='wndus51445@gmail.com',
            subject='📰 [뉴스 데이터 파이프라인] {{ ds }} 일일 리포트',
            html_content="""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                    📰 {{ ds }} 일일 뉴스 리포트
                </h2>

                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #27ae60; margin-top: 0;">✅ 파이프라인 실행 완료</h3>
                    <p><strong>실행 날짜:</strong> {{ ds }}</p>
                    <p><strong>실행 시간:</strong> {{ ts }}</p>
                </div>

                <div style="background-color: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #2980b9; margin-top: 0;">🔄 데이터 처리 흐름</h3>
                    <ol style="line-height: 1.6;">
                        <li><strong>실시간 수집:</strong> RSS → Kafka → Flink (AI 처리)</li>
                        <li><strong>저장:</strong> PostgreSQL + HDFS (/user/realtime/)</li>
                        <li><strong>분석:</strong> Spark 배치 작업</li>
                        <li><strong>리포트:</strong> PDF 생성 및 첨부</li>
                        <li><strong>아카이브:</strong> HDFS (/user/news_archive/{{ ds | replace("-", "/") }}/)</li>
                    </ol>
                </div>

                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #27ae60; margin-top: 0;">📊 처리 결과</h3>
                    <p>• <strong>데이터 소스:</strong> HDFS (/user/realtime/)</p>
                    <p>• <strong>아카이브 위치:</strong> HDFS (/user/news_archive/{{ ds | replace("-", "/") }}/)</p>
                    <p>• <strong>AI 처리:</strong> 카테고리 분류, 키워드 추출, 벡터 임베딩</p>
                    <p>• <strong>분석 엔진:</strong> Apache Spark</p>
                    <p>• <strong>리포트 형식:</strong> PDF (첨부 파일 참조)</p>
                </div>

                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #d68910; margin-top: 0;">📎 첨부 파일</h3>
                    <p>상세한 분석 결과는 첨부된 PDF 파일에서 확인하실 수 있습니다.</p>
                </div>

                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <p style="color: #7f8c8d; font-size: 12px;">
                        이 리포트는 뉴스 데이터 파이프라인에서 자동 생성되었습니다.<br>
                        문의사항이 있으시면 데이터 팀으로 연락주세요.
                    </p>
                </div>
            </div>
            """,
            files=['/opt/airflow/output/daily_reports/{{ ds }}_report.pdf'],
            mime_subtype='mixed',
            doc_md="""
            ### 이메일 리포트 전송
            - HTML 형식의 상세 리포트
            - PDF 파일 첨부
            - 파이프라인 실행 결과 요약
            """
        )

        # 배치 그룹 내 의존성
        check_hdfs_status >> submit_spark_job >> make_pdf_reports >> move_files_to_archive >> send_email_report

    # ========================================
    # 전체 DAG 의존성 설정
    # ========================================
    # 실시간 데이터 수집이 완료된 후 배치 분석 시작
    realtime_group >> batch_group