# ==========================================
# Spark 파티션(Partition)
# ==========================================
# 데이터 분할 단위  
# RDD 또는 DataFrame 구성 요소  
# 각 파티션 → 워커 노드에서 병렬 처리  
# 병렬성 확보, 작업 속도 향상 목적

# 데이터 나누기 → 파티션 생성  
# 파티션 수 늘리기 → repartition(n)  
# 파티션 수 줄이기 → coalesce(n)  
# 파티션 수 확인 → getNumPartitions()  
# 파티션별 데이터 확인 → glom().collect()

# 예시  
# 데이터: 1~100  
# 4개 파티션  
# → 파티션 1: 1~25  
# → 파티션 2: 26~50  
# → 파티션 3: 51~75  
# → 파티션 4: 76~100

# 역할  
# 데이터 분산  
# 처리 병렬화  
# 작업자 간 분배 단위

# 비유  
# 공장 작업  
# 제품 나누기 → 박스 포장  
# 박스 → 여러 작업자에게 전달  
# 작업자 → 병렬로 처리
# ==========================================

from pyspark.sql import SparkSession

# SparkSession 생성
spark = SparkSession.builder.appName("PartitionApp").getOrCreate()
sc = spark.sparkContext

# 1. 1~10까지의 숫자 데이터 생성
numbers = sc.parallelize(list(range(1,11)))

# 기본 파티션 개수 확인
default_partitions = numbers.getNumPartitions()
print(f"기본 파티션 개수: {default_partitions}")

# 파티션 개수를 1개로 변경
repartitioned_data = numbers.repartition(1)
print(f"1개로 변경된 파티션 개수: {repartitioned_data.getNumPartitions()}")

# 2. 기존 데이터 출력
numbers.foreach(lambda x: print(x))

# 파티션 1개로 변경된 데이터 출력
repartitioned_data.foreach(lambda x: print(x))
