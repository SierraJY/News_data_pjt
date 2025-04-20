# ==========================================
# 고객 이탈률 분석을 위한 PySpark RDD 메서드 요약
# ==========================================

# SparkSession           : 스파크 애플리케이션 시작점
# spark.sparkContext     : RDD 연산용 SparkContext

# textFile(path)         : 텍스트 파일 → RDD 변환 (CSV 라인 단위)
# first()                : RDD에서 첫 번째 요소 반환 (헤더 추출용)
# filter(func)           : 조건에 맞는 요소만 필터링
# map(func)              : 각 요소 변환 (ex. 파싱 함수 적용)
# filter(lambda x: x is not None) : 파싱 실패 또는 결측값 제거

# groupByKey()           : 동일 키 기준으로 값 묶기 (ex. 점수대별 이탈 목록)
# mapValues(func)        : 값 리스트만 변환 (평균 계산 등)
# collect()              : RDD → 리스트로 수집 (실행 트리거)
# take(n)                : 앞에서 n개 요소 수집 (미리보기용)

# 주요 분석 항목         : 신용 점수대, 연령대, 카드 유형별 고객 이탈률 (%)
# 이탈률 계산 공식       : 평균(Exited) × 100

# ==========================================

from pyspark.sql import SparkSession

# SparkSession 생성
spark = SparkSession.builder.appName("PartitionPerformanceApp").getOrCreate()
sc = spark.sparkContext

# 1. CSV 파일 로드 및 데이터 확인
# CSV 파일을 RDD로 변환
raw_rdd = sc.textFile("./data/Customer-Churn-Records.csv")

# 헤더 
header = raw_rdd.first()
data_rdd = raw_rdd.filter(lambda line: line != header)

# 헤더 제거 후 상위 5개 데이터
print("\n[헤더 제거 후 상위 5개 데이터]")
for row in data_rdd.take(5):
    print(row)

# 3. 신용 점수(CreditScore)별 고객 이탈률 분석
def parse_credit(line):
    cols = line.split(",")
    if cols[3].strip() == "" or cols[13].strip() == "":
        return None
    credit_score = (int(cols[3]) // 100) * 100
    exited = int(cols[13])
    return (f"{credit_score}점대", exited)

credit_rdd = data_rdd.map(parse_credit).filter(lambda x: x is not None)
credit_avg_rdd = credit_rdd.groupByKey().mapValues(lambda vals: sum(vals)/len(vals)*100)

print("\n[신용 점수대별 평균 이탈률]")
for item in credit_avg_rdd.collect():
    print(item)

# 4. 연령(Age)대별 고객 이탈률 분석
def parse_age(line):
    cols = line.split(",")
    if cols[6].strip() == "" or cols[13].strip() == "":
        return None
    age_group = (int(cols[6]) // 10) * 10
    exited = int(cols[13])
    return (f"{age_group}대", exited)

age_rdd = data_rdd.map(parse_age).filter(lambda x: x is not None)
age_avg_rdd = age_rdd.groupByKey().mapValues(lambda vals: sum(vals)/len(vals)*100)

print("\n[연령대별 평균 이탈률]")
for item in age_avg_rdd.collect():
    print(item)

# 5. 카드 유형(Card Type)별 고객 이탈률 분석
def parse_card(line):
    cols = line.split(",")
    if cols[16].strip() == "" or cols[13].strip() == "":
        return None
    card_type = cols[16].strip()
    exited = int(cols[13])
    return (card_type, exited)

card_rdd = data_rdd.map(parse_card).filter(lambda x: x is not None)
card_avg_rdd = card_rdd.groupByKey().mapValues(lambda vals: sum(vals)/len(vals)*100)

print("\n[카드 유형별 평균 이탈률]")
for item in card_avg_rdd.collect():
    print(item)
