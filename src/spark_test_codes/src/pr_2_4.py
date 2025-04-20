# ==========================================
# 파티션 설정과 병렬 처리 성능 비교
# ==========================================

# - sc.parallelize(range) : RDD 생성 (1~100)
# - getNumPartitions()     : 기본 파티션 개수 확인
# - repartition(2n)        : 파티션 수 증가 (셔플 발생)
# - coalesce(n/2)          : 파티션 수 감소 (셔플 없음, 비용 적음)

# - measure_time(rdd)      : rdd.count() 실행 시간 측정 함수
# - repartition(1/4/8)     : 다양한 파티션 설정
# - 실행 시간 비교 → 병렬성의 영향 확인

# - repartition(n)         : 파티션 재분할 (셔플 발생, 느림)
# - coalesce(n)            : 파티션 축소 (셔플 없음, 효율적)
# - count()                : 전체 요소 개수 계산 → 액션 트리거
# - 병렬 처리 성능은 파티션 수, 워커 수에 따라 달라짐
# ==========================================

import time
from pyspark.sql import SparkSession

# 1. SparkSession 생성
spark = SparkSession.builder.appName("PartitionPerformanceApp").getOrCreate()
sc = spark.sparkContext

# 1. 1~100까지 숫자 데이터 포함 RDD 생성
num100 = sc.parallelize(range(1, 101))

# 2. 기본 파티션 개수 확인
print(f"기본 파티션 개수: {num100.getNumPartitions()}")

# 3. repartition(2n)
repartitioned_rdd = num100.repartition(num100.getNumPartitions()*2)
print(f"repartition(2n) 후 파티션 개수: {repartitioned_rdd.getNumPartitions()}")

# 4. coalesce(n/2)
coalesced_rdd = num100.repartition(repartitioned_rdd.getNumPartitions()//2)
print(f"coalesce(n/2) 후 파티션 개수: {coalesced_rdd.getNumPartitions()}")

# 5. 병렬 처리 성능 비교 함수
def measure_time(rdd):
    start = time.time()
    rdd.count()
    end = time.time()
    return end - start

# 6. 파티션 개수별 실행 시간 측정
rdd1 = num100.repartition(1)
time1 = measure_time(rdd1)
print(f"파티션 1개 실행 시간: {time1:.6f} 초")

rdd4 = num100.repartition(4)
time4 = measure_time(rdd4)
print(f"파티션 4개 실행 시간: {time4:.6f} 초")

rdd8 = num100.repartition(8)
time8 = measure_time(rdd8)
print(f"파티션 8개 실행 시간: {time8:.6f} 초")
