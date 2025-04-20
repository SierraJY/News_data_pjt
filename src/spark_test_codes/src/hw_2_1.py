# ==========================================
# 샘플링 및 데이터 분할 관련 주요 메서드 요약
# ==========================================

# sample(withReplacement, fraction, seed=None)
# - 확률 기반 샘플링
# - withReplacement: 복원(True) / 비복원(False)
# - fraction: 각 요소가 추출될 확률 (0.0 ~ 1.0)
# - seed: 랜덤 시드 (재현 가능성)

# takeSample(withReplacement, num, seed=None)
# - 개수 기반 샘플링
# - 복원 여부와 샘플 개수 지정
# - 반환값: 리스트 (RDD 아님)

# randomSplit(weights, seed=None)
# - RDD → 여러 개로 분할
# - weights: 각 분할 비율 (예: [0.8, 0.2])
# - seed: 랜덤 시드 (분할 재현 가능성)

# count()
# - RDD 요소 개수 계산
# - 샘플링 결과 비교에 사용

# ==========================================

from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("SamplingSplitApp").getOrCreate()
sc = spark.sparkContext


# 1. 1~100까지 숫자 데이터를 RDD로 생성
numbers_rdd = sc.parallelize(range(1, 101))
print(f"원본 데이터 개수: {numbers_rdd.count()}")

# 2. sample() 비복원 방식으로 20% 샘플링
sample_without = numbers_rdd.sample(False, 0.2)
print("비복원 샘플링 결과:", sample_without.collect())

# sample() 복원 방식으로 20% 샘플링
sample_with = numbers_rdd.sample(True, 0.2)
print("복원 샘플링 결과:", sample_with.collect())

# takeSample() 비복원
take_sample_without = numbers_rdd.takeSample(False, 5)
print("takeSample 비복원:", take_sample_without)

# takeSample() 복원
take_sample_with = numbers_rdd.takeSample(True, 5)
print("takeSample 복원:", take_sample_with)

# 3. randomSplit()으로 훈련/테스트 분할
train_rdd, test_rdd = numbers_rdd.randomSplit([0.8, 0.2], seed=42)
print(f"훈련 데이터 개수: {train_rdd.count()}")
print(f"테스트 데이터 개수: {test_rdd.count()}")

# 4. 비교 분석
print(f"비복원 샘플 개수: {sample_without.count()}")
print(f"복원 샘플 개수: {sample_with.count()}")