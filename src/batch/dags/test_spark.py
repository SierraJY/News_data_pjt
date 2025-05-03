from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

# DAG 기본 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
dag = DAG(
    'test_spark',
    default_args=default_args,
    description='Spark 마스터-워커 테스트',
    schedule_interval=None,
    catchup=False,
    tags=['example'],
)

# 1. Spark 마스터 웹 UI 연결 확인
check_master = BashOperator(
    task_id='check_spark_master',
    bash_command='''
    echo "Spark 마스터 연결 확인 중..." &&
    curl -s http://spark-master:8080/ > /tmp/spark_master_output.txt &&
    if grep -E "Spark Master|Status: ALIVE|Running|Active|alive" /tmp/spark_master_output.txt; then
        echo "Spark 마스터 연결 성공!"
    else
        echo "Spark 마스터 연결 실패. 출력 내용:" &&
        cat /tmp/spark_master_output.txt &&
        exit 1
    fi
    ''',
    dag=dag,
)

# 2. Spark 워커 웹 UI 연결 확인
check_worker = BashOperator(
    task_id='check_spark_worker',
    bash_command='''
    echo "Spark 워커 연결 확인 중..." &&
    curl -s http://spark-worker:8081/ > /tmp/spark_worker_output.txt &&
    if grep -E "Spark Worker|ALIVE|Running|Active|alive" /tmp/spark_worker_output.txt; then
        echo "Spark 워커 연결 성공!"
    else
        echo "Spark 워커 연결 실패. 출력 내용:" &&
        cat /tmp/spark_worker_output.txt &&
        exit 1
    fi
    ''',
    dag=dag,
)

# 3. 간단한 Spark 파이썬 스크립트 생성
create_spark_script = BashOperator(
    task_id='create_spark_script',
    bash_command='''
    # Airflow 컨테이너 내에 스크립트 생성
    mkdir -p /opt/airflow/dags/scripts &&
    cat > /opt/airflow/dags/scripts/simple_spark_test.py << 'EOL'
from pyspark.sql import SparkSession
import random
import time
import os

# 현재 실행 환경 정보 출력 (디버깅용)
print("현재 작업 디렉토리:", os.getcwd())
print("스크립트 경로:", __file__)
print("디렉토리 내용:", os.listdir("."))

# 타임스탬프로 앱 이름 생성 (중복 방지)
timestamp = int(time.time())
app_name = f"SparkTest-{timestamp}"

# Spark 세션 생성
print("Spark 세션 생성 중...")
try:
    spark = SparkSession.builder \
        .appName(app_name) \
        .master("spark://spark-master:7077") \
        .getOrCreate()
    
    # Spark 버전 및 설정 정보 출력
    print(f"Spark 버전: {spark.version}")
    print("Spark 설정:")
    for k, v in spark.sparkContext.getConf().getAll():
        print(f"  {k}: {v}")
    
    # 간단한 데이터 처리
    print("간단한 데이터 처리 테스트 중...")
    data = [(i, random.randint(1, 100)) for i in range(10)]
    df = spark.createDataFrame(data, ["id", "value"])
    print("데이터프레임 생성 완료:")
    df.show()
    
    # 간단한 집계 연산 수행
    print("집계 연산 수행 중...")
    result = df.agg({"value": "sum"}).collect()[0][0]
    print(f"합계: {result}")
    
    # 정상 종료 확인
    print("Spark 세션 종료 중...")
    spark.stop()
    print("Spark 테스트 완료!")
except Exception as e:
    print(f"오류 발생: {str(e)}")
    import traceback
    traceback.print_exc()
    raise
EOL
    
    # 스크립트 파일 권한 설정
    chmod 755 /opt/airflow/dags/scripts/simple_spark_test.py
    
    # 디버깅용 정보 출력
    echo "스크립트 경로: /opt/airflow/dags/scripts/simple_spark_test.py"
    ls -la /opt/airflow/dags/scripts/
    ''',
    dag=dag,
)

# 4. Spark 작업 제출 (파일 경로 수정)
run_spark_job = SparkSubmitOperator(
    task_id='run_spark_job',
    # Airflow 컨테이너 내부 경로 사용
    application='/opt/airflow/dags/scripts/test_simple_spark.py',
    conn_id='spark_default',
    verbose=True,
    conf={
        'spark.driver.memory': '1g',
        'spark.executor.memory': '1g',
        'spark.executor.cores': '1',
        'spark.submit.deployMode': 'client',
        'spark.app.name': 'airflow-spark-test',
        'spark.master': 'spark://spark-master:7077',
    },
    dag=dag,
)

# 5. 결과 확인
check_results = BashOperator(
    task_id='check_results',
    bash_command='''
    echo "Spark 작업 로그 확인 중..." &&
    echo "Spark 작업이 성공적으로 실행되었습니다!"
    ''',
    dag=dag,
)

# 작업 순서 정의
check_master >> check_worker >> create_spark_script >> run_spark_job >> check_results
