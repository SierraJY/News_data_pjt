# ==========================================
# PySpark 주요 구성요소 및 메서드 설명
# ==========================================

# SparkSession         : 스파크 진입점 역할을 하는 클래스
# .builder             : 세션 설정 시작 객체
# .appName(...)        : 앱 이름 지정
# .getOrCreate()       : 기존 세션 반환 or 새로 생성

# spark.sparkContext   : RDD 연산 등을 위한 저수준 API(SparkContext)

# sc.parallelize(...)  : 리스트 등 파이썬 객체 → RDD 변환 (분산 데이터 생성)
# rdd.collect()        : RDD → 리스트로 수집 (드라이버 프로그램으로 가져옴)
# rdd.map(func)        : 요소 단위 변환 (각 요소에 함수 적용)
# rdd.filter(func)     : 조건에 따라 요소 필터링
# rdd.count()          : 요소 개수 반환

# ==========================================


from pyspark.sql import SparkSession  # 스파크 세션 생성

spark = SparkSession.builder.appName("WordLengthApp").getOrCreate()
sc = spark.sparkContext

# 1. 단어 길이 변환 및 필터링
words = sc.parallelize(["Spark", "Parallel", "Machine", "Learning", "Hadoop", "Kafka", "Big Data"])
print(words.collect())

word_lengths = words.map(lambda word: len(word))
print(word_lengths.collect())

long_words = words.filter(lambda word: len(word) >= 6)
print(long_words.collect())

long_words_count = long_words.count()
print(f"6글자 이상 단어 개수: {long_words_count}")

# 2. 짝수/홀수 필터링
numbers = sc.parallelize(range(1, 21))

even = numbers.filter(lambda x: x % 2 == 0)
print("짝수:", even.collect())

odd = numbers.filter(lambda x: x % 2 != 0)
print("홀수:", odd.collect())

# 3. 소문자 변환 및 "is" 포함 문장 필터링
sentences = sc.parallelize([
    "Spark is a powerful analytics engine",
    "Big Data is transforming industries",
    "Data Science is revolutionizing decision making",
    "Machine Learning and AI are the future"
])

lower = sentences.map(lambda line: line.lower())
print("소문자 변환:", lower.collect())

contains_is = sentences.filter(lambda line: "is" in line.lower())
print('"is" 포함 문장:', contains_is.collect())
