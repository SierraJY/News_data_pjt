import sys
import argparse
import os
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, when, length, substring, to_date, input_file_name
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, DoubleType

def main(report_date_str):

    # WebHDFS HTTP 경로로 변경 (9870 포트 사용)
    INPUT_PATH = "webhdfs://namenode:9870/user/realtime/news_*.json"
    ARCHIVE_DIR = "/opt/airflow/output/daily_reports"
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    spark = SparkSession.builder \
        .appName("DailyNewsReportHDFS") \
        .master("spark://spark-master:7077") \
        .config("spark.executor.memory", "1g") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.hadoop.fs.defaultFS", "webhdfs://namenode:9870") \
        .config("spark.hadoop.fs.webhdfs.impl", "org.apache.hadoop.hdfs.web.WebHdfsFileSystem") \
        .getOrCreate()

    try:
        # 스키마 정의
        schema = StructType([
            StructField("title", StringType(), True),
            StructField("content", StringType(), True),
            StructField("url", StringType(), True),
            StructField("original_category", StringType(), True),
            StructField("ai_category", StringType(), True),
            StructField("keywords", ArrayType(StringType()), True),
            StructField("embedding", ArrayType(DoubleType()), True),
            StructField("source", StringType(), True),
            StructField("writer", StringType(), True),
            StructField("publish_date", StringType(), True)
        ])

        # HDFS에서 JSON 파일들 직접 읽기
        print(f"HDFS에서 JSON 파일 읽기 시작: {INPUT_PATH}")
        
        try:
            # multiLine=True로 설정하여 각 파일이 하나의 JSON 객체로 처리되도록 함
            df = spark.read \
                .option("multiLine", "true") \
                .option("mode", "PERMISSIVE") \
                .schema(schema) \
                .json(INPUT_PATH)
            
            # 파일 이름도 포함시켜서 디버깅에 활용
            df = df.withColumn("source_file", input_file_name())
            
        except Exception as e:
            print(f"HDFS에서 파일을 읽을 수 없습니다: {e}")
            print("빈 DataFrame으로 처리를 계속합니다.")
            df = spark.createDataFrame([], schema)

        # publish_date_only 생성 (substring + to_date)
        df = df.withColumn("publish_date_only", to_date(substring(col("publish_date"), 1, 10), "yyyy-MM-dd"))

        total_count = df.count()
        print(f"총 {total_count}개의 뉴스 데이터를 HDFS에서 로드했습니다.")

        if total_count == 0:
            print("HDFS에서 읽어온 데이터가 없습니다.")
            # 빈 리포트 생성
            report_data = {
                "meta": {
                    "date": report_date_str,
                    "total_articles": 0,
                    "top_category": "N/A",
                    "top_source": "N/A",
                    "top_keyword": "N/A",
                    "data_source": "HDFS",
                    "input_path": INPUT_PATH
                },
                "category_counts": [],
                "original_category_counts": [],
                "source_counts": [],
                "keyword_counts": [],
                "length_distribution": []
            }
            
            report_file_path = f"{ARCHIVE_DIR}/{report_date_str}_report.json"
            with open(report_file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            print(f"빈 리포트를 {report_file_path}에 저장했습니다.")
            return

        # 날짜별 필터링
        df_filtered = df.filter(col("publish_date_only") == report_date_str)
        filtered_count = df_filtered.count()

        if filtered_count == 0:
            # 가장 최근 날짜의 데이터 사용
            latest_date = df.agg({"publish_date_only": "max"}).collect()[0][0]
            if not latest_date:
                print("유효한 날짜가 없습니다.")
                sys.exit(0)
            print(f"요청된 날짜 {report_date_str}의 데이터가 없습니다.")
            print(f"대신 가장 최근 날짜 {latest_date}의 데이터를 처리합니다.")
            df_filtered = df.filter(col("publish_date_only") == latest_date)
            filtered_count = df_filtered.count()
            report_date_str = str(latest_date)

        if filtered_count > 0:
            print(f"분석 대상 기사 수: {filtered_count}")
            
            # 각종 통계 계산
            category_counts = df_filtered.groupBy("ai_category").count().orderBy(col("count").desc())
            original_category_counts = df_filtered.groupBy("original_category").count().orderBy(col("count").desc())
            source_counts = df_filtered.groupBy("source").count().orderBy(col("count").desc())

            # 키워드 분석
            keywords_df = df_filtered.select("url", explode(col("keywords")).alias("keyword"))
            keyword_counts = keywords_df.groupBy("keyword").count().orderBy(col("count").desc())

            # 기사 길이별 분류
            df_filtered = df_filtered.withColumn(
                "content_length_category",
                when(length(col("content")) < 500, "짧은 기사")
                .when(length(col("content")) < 2000, "중간 기사")
                .otherwise("긴 기사")
            )
            length_distribution = df_filtered.groupBy("content_length_category").count().orderBy("content_length_category")

            # 리포트 데이터 구성
            report_data = {
                "meta": {
                    "date": report_date_str,
                    "total_articles": filtered_count,
                    "top_category": category_counts.first()["ai_category"] if not category_counts.isEmpty() else "N/A",
                    "top_source": source_counts.first()["source"] if not source_counts.isEmpty() else "N/A",
                    "top_keyword": keyword_counts.first()["keyword"] if not keyword_counts.isEmpty() else "N/A",
                    "data_source": "HDFS",
                    "input_path": INPUT_PATH
                },
                "category_counts": [{"category": row["ai_category"], "count": row["count"]} for row in category_counts.collect()],
                "original_category_counts": [{"category": row["original_category"], "count": row["count"]} for row in original_category_counts.collect()],
                "source_counts": [{"source": row["source"], "count": row["count"]} for row in source_counts.collect()],
                "keyword_counts": [{"keyword": row["keyword"], "count": row["count"]} for row in keyword_counts.collect()[:100]],
                "length_distribution": [{"category": row["content_length_category"], "count": row["count"]} for row in length_distribution.collect()]
            }

            # 리포트 저장
            report_file_path = f"{ARCHIVE_DIR}/{report_date_str}_report.json"
            with open(report_file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)

            print(f"분석 결과를 {report_file_path}에 저장했습니다.")
            print(f"총 기사 수: {filtered_count}")
            print(f"상위 카테고리: {report_data['meta']['top_category']}")
            print(f"상위 언론사: {report_data['meta']['top_source']}")
            print(f"상위 키워드: {report_data['meta']['top_keyword']}")
            print(f"데이터 소스: HDFS ({INPUT_PATH})")

            print("카테고리별 기사 수:")
            for item in report_data["category_counts"]:
                print(f"  - {item['category']}: {item['count']}")
        else:
            print("분석할 데이터가 없습니다.")

    except Exception as e:
        print(f"데이터 처리 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spark를 이용한 일일 뉴스 리포트 생성 (HDFS 버전)")
    parser.add_argument("--date", required=True, help="보고서 기준 날짜 (YYYY-MM-DD)")
    args = parser.parse_args()

    main(args.date)