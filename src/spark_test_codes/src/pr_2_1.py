# ==========================================
# Spark RDD 주요 개념 및 연산 요약
# ==========================================

# SparkSession            : 스파크 애플리케이션 시작점 (최신 방식)
# spark.sparkContext      : RDD 연산용 SparkContext 추출

# parallelize(data)       : 파이썬 리스트 → RDD 변환
# textFile(path)          : 텍스트 파일 로드 → RDD 생성 (한 줄 = 하나의 요소)

# collect()               : RDD → 리스트 수집 (실제 연산 트리거)
# filter(func)            : 조건 만족 요소 필터링
# map(func)               : 요소 단위 변환
# flatMap(func)           : 요소를 여러 개로 펼쳐서 반환 (ex. 문장 → 단어 리스트)

# Lazy Evaluation         : RDD 변환 연산(map, filter 등)은 즉시 실행되지 않음
#                         → collect(), count(), saveAsTextFile() 등 액션 호출 시 실행

# 예시 흐름
# - 숫자 리스트 생성 → RDD 변환
# - 짝수 필터링, 두 배 변환
# - 텍스트 파일 로드 → 단어 분리
# - 조건문 필터링 → Spark 포함 문장 추출
# - map + filter → lazy 연산 정의 후 collect로 실행

# ==========================================

from pyspark.sql import SparkSession

# SparkSession 생성 (최신 진입점)
spark = SparkSession.builder.appName("RDDTransformations").getOrCreate()
# RDD 작업을 위해 SparkContext 추출
sc = spark.sparkContext

# 1. 1~5까지의 리스트 데이터를 RDD로 변환
numbers_rdd = sc.parallelize(range(1, 6))
print(numbers_rdd.collect())

# 2. 짝수 데이터만 필터링
num_filtered_rdd = numbers_rdd.filter(lambda x: x % 2 == 0)
print(num_filtered_rdd.collect())

# 3. 모든 숫자를 2배로 변환
doubled_rdd = numbers_rdd.map(lambda x: x * 2)
print(doubled_rdd.collect())

# 4. 외부 텍스트 파일 로드
text_rdd = sc.textFile("./data/pr_1_3_data.txt")
print(text_rdd.collect())

# 5. "Spark"가 포함된 문장 필터링
filtered_rdd = text_rdd.filter(lambda line: "Spark" in line)
print(filtered_rdd.collect())

# 6. 문장을 단어 단위로 분해
words_rdd = text_rdd.flatMap(lambda line: line.split(" "))
print(words_rdd.collect())

# 7. Lazy Evaluation 실습
lazy_rdd = numbers_rdd.map(lambda x: x * 2).filter(lambda x: x > 5)

# 8. 생성 완료 후 잠시 대기
print("RDD 생성 완료. 아직 연산이 실행되지 않았습니다.")

# 9. 실제 연산 실행 (collect 호출)
print(lazy_rdd.collect())
