# ==========================================
# RDD 연산 방식별 성능 비교
# ==========================================

# filter(func)         
# - 요소 조건 필터링
# - 요소별 개별 처리 (많은 함수 호출 발생)

# map(func)            
# - 요소 단위 변환
# - 각 요소에 1:1 함수 적용

# flatMap(func)        
# - 요소 → 0개 이상 결과로 변환
# - 필터 + 변환을 한 번에 수행 가능

# mapPartitions(func)  
# - 파티션 단위 연산
# - 반복자(iterator)를 입력으로 받아, 한번에 처리 (성능 최적화에 유리)

# collect()            
# - 연산 결과를 드라이버로 수집
# - 전체 결과 계산을 실제로 트리거함

# measure_time(func)   
# - 실행 시간 측정용 사용자 정의 함수
# - lazy evaluation 이후 성능 측정 목적

# ==========================================


import time
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("RDDOptimization").getOrCreate()
sc = spark.sparkContext

# 1. 파티션 개수 지정
num_partitions = 8

# 2. 1~1,000,000까지의 숫자 데이터를 포함하는 RDD 생성
rdd = sc.parallelize(range(1, 1000001), num_partitions)

# 3. 수행 시간 측정 함수 정의
def measure_time(fn):
    start = time.time()
    result = fn()
    end = time.time()
    return result, end - start

# 4. map+filter 연산
map_filter_result, t1 = measure_time(lambda: rdd.filter(lambda x: x % 2 == 0).map(lambda x: x * 2).collect())
print("[map + filter] 개수:", len(map_filter_result))
print("[map + filter] 샘플:", map_filter_result[:5])
print("[map + filter] 시간:", round(t1, 4), "초")

# 5. flatMap 연산
flatmap_result, t2 = measure_time(lambda: rdd.flatMap(lambda x: [x * 2] if x % 2 == 0 else []).collect())
print("[flatMap] 개수:", len(flatmap_result))
print("[flatMap] 샘플:", flatmap_result[:5])
print("[flatMap] 시간:", round(t2, 4), "초")

# 6. mapPartitions 연산
def transform_partition(iterator):
    return (x * 2 for x in iterator if x % 2 == 0)

mappart_result, t3 = measure_time(lambda: rdd.mapPartitions(transform_partition).collect())
print("[mapPartitions] 개수:", len(mappart_result))
print("[mapPartitions] 샘플:", mappart_result[:5])
print("[mapPartitions] 시간:", round(t3, 4), "초")
