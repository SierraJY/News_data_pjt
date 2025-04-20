# ==========================================
# PySpark 주요 구성요소 및 메서드 설명 (파일 입출력 + 문자열 처리 중심)
# ==========================================

# SparkSession         : 스파크 애플리케이션의 진입점 (DataFrame, RDD 작업 시작)
# .builder             : 세션 설정 시작 객체
# .appName(...)        : 스파크 애플리케이션 이름 지정
# .getOrCreate()       : 기존 세션 반환 or 새로 생성

# spark.sparkContext   : 저수준 API (RDD 연산 등) 접근용

# sc.textFile(path)    : 외부 텍스트 파일을 RDD로 불러옴 (한 줄 = 하나의 요소)
# rdd.collect()        : RDD 데이터를 리스트로 수집 (드라이버 프로그램으로 전송)
# rdd.map(func)        : 요소 단위 변환 (함수 적용)
# rdd.upper() / lower(): 문자열 대소문자 변환 (파이썬 문자열 메서드 사용 가능)
# len(rdd.collect())   : 전체 줄 수 확인 (수집한 후 개수 셈)

# ==========================================


from pyspark.sql import SparkSession

# SparkSession 생성
spark = SparkSession.builder.appName("LoadExternalFileApp").getOrCreate()
sc = spark.sparkContext

# 1. 텍스트 파일 로드
text_data = sc.textFile("./data/pr_1_3_data.txt")

# 2. 전체 데이터 확인
print(text_data.collect())

# 3. 전체 줄 개수 확인
print(len(text_data.collect()))

# 4. 모든 문장을 대문자로 변환 후 출력
upper_case_data = text_data.map(lambda line: line.upper())
print(upper_case_data.collect())

# 5. 모든 문장을 소문자로 변환 후 출력
lower_case_data = text_data.map(lambda line: line.lower())
print(lower_case_data.collect())

# 6. 각 문장의 길이 출력
line_lengths = text_data.map(lambda line: len(line))
print(line_lengths.collect())
