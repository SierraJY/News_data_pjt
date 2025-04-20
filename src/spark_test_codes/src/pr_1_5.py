from pyspark.sql import SparkSession

# SparkSession 생성
spark = SparkSession.builder.appName("DataFilterApp").getOrCreate()
sc = spark.sparkContext

# 1. 텍스트 파일 로드 및 데이터 확인
text_data = sc.textFile("./data/pr_1_3_data.txt")
print(text_data.collect())

# 2. "data"가 포함된 문장만 출력
contains_data = text_data.filter(lambda line: "data" in line.lower())
print(contains_data.collect())

# 3. "ai"가 포함된 문장만 출력
contains_ai = text_data.filter(lambda line: "ai" in line.lower())
print(contains_ai.collect())

# 4. "data"가 포함된 문장의 개수
print("data 포함 문장 수:", contains_data.count())

# 5. "ai"가 포함된 문장의 개수
print("ai 포함 문장 수:", contains_ai.count())

# 6. "Big"으로 시작하는 문장
starts_with_big = text_data.filter(lambda line: line.startswith("Big"))
print(starts_with_big.collect())

# 7. "future"로 끝나는 문장
ends_with_future = text_data.filter(lambda line: line.endswith("future"))
print(ends_with_future.collect())