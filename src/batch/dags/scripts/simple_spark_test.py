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
    spark = SparkSession.builder         .appName(app_name)         .master("spark://spark-master:7077")         .getOrCreate()
    
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
