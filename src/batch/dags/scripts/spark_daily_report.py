import sys
import argparse
import os
import json
import glob
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, when, length, substring, to_date
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, DoubleType

def main(report_date_str):

    INPUT_PATH = "/opt/airflow/data/realtime/news_*.json"
    ARCHIVE_DIR = "/opt/airflow/output/daily_reports"
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    spark = SparkSession.builder \
        .appName("DailyNewsReport") \
        .master("spark://spark-master:7077") \
        .config("spark.executor.memory", "1g") \
        .getOrCreate()

    try:
        # JSON 파일들 파이썬 리스트로 수집
        json_data = []
        for file_path in glob.glob(INPUT_PATH):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if isinstance(content, list):
                    json_data.extend(content)
                elif isinstance(content, dict):
                    json_data.append(content)

        if not json_data:
            print("JSON 파일이 비어 있거나 로드할 수 없습니다.")
            sys.exit(0)

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

        df = spark.createDataFrame(json_data, schema)

        # publish_date_only 생성 (substring + to_date)
        df = df.withColumn("publish_date_only", to_date(substring(col("publish_date"), 1, 10), "yyyy-MM-dd"))

        if df.count() == 0:
            print("데이터프레임이 비어 있습니다.")
            sys.exit(0)

        print(f"총 {df.count()}개의 뉴스 데이터를 로드했습니다.")

        df_filtered = df.filter(col("publish_date_only") == report_date_str)
        filtered_count = df_filtered.count()

        if filtered_count == 0:
            latest_date = df.agg({"publish_date_only": "max"}).collect()[0][0]
            if not latest_date:
                print("유효한 날짜가 없습니다.")
                sys.exit(0)
            print(f"대신 가장 최근 날짜 {latest_date}의 데이터를 처리합니다.")
            df_filtered = df.filter(col("publish_date_only") == latest_date)
            filtered_count = df_filtered.count()
            report_date_str = str(latest_date)

        if filtered_count > 0:
            category_counts = df_filtered.groupBy("ai_category").count().orderBy(col("count").desc())
            original_category_counts = df_filtered.groupBy("original_category").count().orderBy(col("count").desc())
            source_counts = df_filtered.groupBy("source").count().orderBy(col("count").desc())

            keywords_df = df_filtered.select("url", explode(col("keywords")).alias("keyword"))
            keyword_counts = keywords_df.groupBy("keyword").count().orderBy(col("count").desc())

            df_filtered = df_filtered.withColumn(
                "content_length_category",
                when(length(col("content")) < 500, "짧은 기사")
                .when(length(col("content")) < 2000, "중간 기사")
                .otherwise("긴 기사")
            )
            length_distribution = df_filtered.groupBy("content_length_category").count().orderBy("content_length_category")

            report_data = {
                "meta": {
                    "date": report_date_str,
                    "total_articles": filtered_count,
                    "top_category": category_counts.first()["ai_category"] if not category_counts.isEmpty() else "N/A",
                    "top_source": source_counts.first()["source"] if not source_counts.isEmpty() else "N/A",
                    "top_keyword": keyword_counts.first()["keyword"] if not keyword_counts.isEmpty() else "N/A"
                },
                "category_counts": [{"category": row["ai_category"], "count": row["count"]} for row in category_counts.collect()],
                "original_category_counts": [{"category": row["original_category"], "count": row["count"]} for row in original_category_counts.collect()],
                "source_counts": [{"source": row["source"], "count": row["count"]} for row in source_counts.collect()],
                "keyword_counts": [{"keyword": row["keyword"], "count": row["count"]} for row in keyword_counts.collect()[:100]],
                "length_distribution": [{"category": row["content_length_category"], "count": row["count"]} for row in length_distribution.collect()]
            }

            report_file_path = f"{ARCHIVE_DIR}/{report_date_str}_report.json"
            with open(report_file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)

            print(f"분석 결과를 {report_file_path}에 저장했습니다.")
            print(f"총 기사 수: {filtered_count}")
            print(f"상위 카테고리: {report_data['meta']['top_category']}")
            print(f"상위 언론사: {report_data['meta']['top_source']}")
            print(f"상위 키워드: {report_data['meta']['top_keyword']}")

            print("카테고리별 기사 수:")
            for item in report_data["category_counts"]:
                print(f"  - {item['category']}: {item['count']}")
        else:
            print("저장할 데이터가 없습니다.")

    except Exception as e:
        print(f"데이터 처리 실패: {e}")
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spark를 이용한 일일 뉴스 리포트 생성")
    parser.add_argument("--date", required=True, help="보고서 기준 날짜 (YYYY-MM-DD)")
    args = parser.parse_args()

    main(args.date)
