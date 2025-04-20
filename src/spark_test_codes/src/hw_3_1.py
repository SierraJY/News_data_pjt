# ==========================================
# PySpark DataFrame 처리 주요 메서드 요약
# ==========================================

# createDataFrame(data, schema=None)
# - RDD, 리스트, pandas DataFrame 등으로부터 Spark DataFrame 생성
# - schema: 컬럼명 리스트 또는 StructType 스키마 객체 

# printSchema()
# - DataFrame의 스키마(구조) 출력
# - 각 컬럼명, 데이터 타입, null 허용 여부 표시

# withColumn(colName, col)
# - 새 컬럼 추가 또는 기존 컬럼 대체
# - colName: 새 컬럼명
# - col: 컬럼 표현식

# col(colName)
# - 컬럼을 참조하는 Column 객체 생성
# - 다양한 연산과 함께 사용 가능

# cast(dataType)
# - 컬럼의 데이터 타입 변환
# - IntegerType(), StringType() 등의 타입으로 변환

# to_date(col, format)
# - 문자열을 날짜 형식으로 변환
# - format: 날짜 형식 지정 (예: "dd-MM-yyyy")

# show(n=20, truncate=True)
# - DataFrame의 내용을 콘솔에 출력
# - n: 출력할 행 수
# - truncate: 긴 값 잘림 여부
# ==========================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date
from pyspark.sql.types import IntegerType

spark = SparkSession.builder.appName("CastAndDateFormat").getOrCreate()

# 1. 데이터 준비
data = [
    ("Alice", "25-12-2023", "3500"),
    ("Bob", "10-01-2024", "4500"),
    ("Charlie", "05-02-2024", "5000"),
    ("David", "15-03-2024", "6000")
]

columns = ["Customer", "OrderDate", "Price"]

# DataFrame 생성
df = spark.createDataFrame(data, columns)

# 2. 원본 스키마 출력
print("원본 스키마:")
df.printSchema()

# 3. Price 컬럼을 정수형으로 변환하여 새 컬럼 "Price_Int" 추가
df = df.withColumn("Price_Int", col("Price").cast(IntegerType()))

# 4. OrderDate 문자열을 날짜(Date) 형식으로 변환하여 새 컬럼 추가
df = df.withColumn("Order_Date_Format", to_date(col("OrderDate"), "dd-MM-yyyy"))

# 5. 변경된 스키마 출력
print("변환된 스키마:")
df.printSchema()

# 7. 최종 결과 출력
df.show(truncate=False)
