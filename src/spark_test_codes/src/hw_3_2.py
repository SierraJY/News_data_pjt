# ==========================================
# Spark DataFrame API와 Spark SQL 비교 관련 주요 메서드 요약
# ==========================================

# read.option().csv() 
# - CSV 파일을 Spark DataFrame으로 로드
# - option("header", True): 첫 행을 헤더로 인식
# - option("inferSchema", True): 데이터 타입 자동 추론

# filter(조건식)
# - DataFrame에서 조건에 맞는 행만 필터링
# - SQL의 WHERE 절과 동일한 기능

# col(컬럼명)
# - 특정 컬럼을 참조하는 Column 객체 생성
# - 필터링, 계산 등 컬럼 연산에 사용

# count()
# - DataFrame의 행 수 계산
# - 결과는 정수 값으로 반환

# createOrReplaceTempView(뷰이름)
# - DataFrame을 SQL 쿼리에서 사용할 수 있는 임시 뷰로 등록
# - 세션 종료 시 자동으로 제거됨

# spark.sql(쿼리문)
# - SQL 문을 실행하여 결과를 DataFrame으로 반환
# - 등록된 임시 뷰에 대해 쿼리 수행 가능

# collect()
# - DataFrame의 모든 행을 드라이버 프로그램으로 가져옴
# - 결과가 작을 때만 사용 권장 (대용량 데이터에는 부적합)

# ==========================================
# 학습 방향 및 개념
# ==========================================
# - Spark는 두 가지 주요 데이터 처리 방식 제공:
#   1) DataFrame API: 프로그래밍 방식으로 데이터 처리
#   2) Spark SQL: SQL 문법으로 직관적인 데이터 처리
#
# - 두 방식의 비교:
#   * 성능: 내부적으로 동일한 실행 계획으로 변환되어 유사한 성능
#   * 사용성: SQL은 SQL 경험자에게 직관적, DataFrame API는 프로그래머에게 친숙
#   * 복잡성: 복잡한 데이터 처리는 DataFrame API가 유리할 수 있음
#
# - 성능 측정 방법:
#   * time 모듈을 활용한 실행 시간 측정
#   * 동일한 조건에서 여러 번 실행하여 평균 성능 비교 권장
# ==========================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import time
spark = SparkSession.builder.appName("DataFrameVsSQL").getOrCreate()

# 1. CSV 파일 로딩
df = spark.read.option("header", True).option("inferSchema", True).csv("../data/people.csv")

# 2. DataFrame API 방식
start_df = time.time()
count_df = df.filter(col("Age") >= 30).count()
end_df = time.time()
elapsed_df = end_df - start_df

print(f"DataFrame API 방식 - 30세 이상 인원 수: {count_df}")
print(f"DataFrame API 처리 시간: {elapsed_df:.6f}초")

# 3. Spark SQL 방식
df.createOrReplaceTempView("people") # 뷰 등록

start_sql = time.time()
count_sql = spark.sql("SELECT COUNT(*) FROM people WHERE Age >= 30").collect()[0][0]
end_sql = time.time()
elapsed_sql = end_sql - start_sql

print(f"Spark SQL 방식 - 30세 이상 인원 수: {count_sql}")
print(f"Spark SQL 처리 시간: {elapsed_sql:.6f}초")

# 4. 성능 비교
if elapsed_df < elapsed_sql:
    print("DataFrame API 방식이 더 빠릅니다.")
elif elapsed_sql < elapsed_df:
    print("Spark SQL 방식이 더 빠릅니다.")
else:
    print("두 방식의 성능이 거의 동일합니다.")