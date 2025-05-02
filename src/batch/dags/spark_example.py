from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 스크립트 파일 생성을 위한 경로 설정
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
spark_script_path = os.path.join(scripts_dir, "spark_job.py")

# PySpark 스크립트 작성 함수
def create_spark_script():
    os.makedirs(scripts_dir, exist_ok=True)
    
    with open(spark_script_path, 'w') as f:
        f.write('''
from pyspark.sql import SparkSession
import matplotlib.pyplot as plt
import numpy as np
import os

# Spark 세션 생성
spark = SparkSession.builder \\
    .appName("Simple Spark Example") \\
    .master("spark://spark-master:7077") \\
    .config("spark.executor.memory", "1g") \\
    .getOrCreate()

# 샘플 데이터 생성
data = [(i, i * 2) for i in range(1, 11)]
df = spark.createDataFrame(data, ["x", "y"])

# 데이터 출력
print("생성된 데이터:")
df.show()

# 간단한 변환
df2 = df.withColumn("y_squared", df.y * df.y)
print("변환된 데이터:")
df2.show()

# 결과를 파이썬 객체로 변환
pandas_df = df2.toPandas()

# 시각화
plt.figure(figsize=(10, 6))
plt.scatter(pandas_df['x'], pandas_df['y'], color='blue', label='y = 2x')
plt.scatter(pandas_df['x'], pandas_df['y_squared'], color='red', label='y = 2x²')
plt.title('간단한 Spark 데이터 시각화')
plt.xlabel('X 값')
plt.ylabel('Y 값')
plt.legend()
plt.grid(True)

# 결과 디렉토리 확인 및 생성
output_dir = "/opt/airflow/output"
os.makedirs(output_dir, exist_ok=True)

# 그래프 저장
plt.savefig(f"{output_dir}/spark_plot.png")
print(f"그래프가 {output_dir}/spark_plot.png에 저장되었습니다.")

# Spark 세션 종료
spark.stop()
''')
    print(f"Spark 스크립트가 {spark_script_path}에 생성되었습니다.")
    return spark_script_path

with DAG(
    'spark_example',
    default_args=default_args,
    description='A simple Spark example DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['example', 'spark'],
) as dag:
    
    create_script_task = PythonOperator(
        task_id='create_spark_script',
        python_callable=create_spark_script,
    )
    
    spark_task = SparkSubmitOperator(
        task_id='spark_job',
        application=spark_script_path,
        conn_id='spark_default',
        verbose=True,
        conf={
            'spark.master': 'spark://spark-master:7077',
            'spark.executor.memory': '1g',
            'spark.executor.cores': '1',
            'spark.driver.memory': '1g'
        }
    )
    
    create_script_task >> spark_task 