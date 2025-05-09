"""
Flink 컨슈머 메인 애플리케이션
- Kafka에서 뉴스 데이터를 소비하여 처리하는 Flink 애플리케이션
- 전처리, 임베딩 생성, 키워드 추출, 데이터베이스 저장 기능
"""

import os
import sys
import json
import traceback
from datetime import datetime
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.datastream.functions import MapFunction
from dotenv import load_dotenv

# 현재 경로 추가 - 도커 컨테이너 환경에 맞게 조정
sys.path.append('/opt/workspace')

# 로컬 모듈 임포트 (현재 디렉터리에서 임포트)
from db_handler import save_to_postgresql, test_database_connection
from preprocess_openai import (
    preprocess_content,
    transform_extract_keywords,
    transform_to_embedding,
    transform_classify_category
)

# 환경 변수 로드
load_dotenv()

class NewsProcessor(MapFunction):
    """Kafka에서 수신한 뉴스 데이터를 처리하는 맵 함수"""
    
    def map(self, message):
        try:
            print(f"[DEBUG] 새 메시지 수신: {message}")  # 메시지 수신 로그 추가
            
            # JSON 문자열을 파이썬 딕셔너리로 변환
            data = json.loads(message)
            
            # 메시지 기본 정보 출력
            print(f"[Processing] {data.get('title', 'No title')}")
            
            # 필요한 필드 추출
            title = data.get('title', '')
            content = data.get('content', '')
            url = data.get('url', '')
            original_category = data.get('category', '')
            source = data.get('source', '')
            writer = data.get('writer', '')
            original_keywords = data.get('keywords', [])
            write_date = data.get('write_date','')
            
            # 데이터 전처리 및 변환
            if content:
                print(f"[DEBUG] 콘텐츠 처리 시작: {title[:50]}...")
                
                preprocessed_content = preprocess_content(content)
                
                # AI 카테고리 분류
                ai_category = transform_classify_category(preprocessed_content)
                print(f"[DEBUG] AI 카테고리 분류: {ai_category}")
                
                # 키워드 추출 - 원본 키워드가 있으면 유지, 없으면 AI로 추출
                if not original_keywords:
                    keywords = transform_extract_keywords(preprocessed_content)
                else:
                    keywords = original_keywords
                print(f"[DEBUG] 추출된 키워드: {keywords}")
                
                # 벡터 임베딩 생성
                embedding = transform_to_embedding(preprocessed_content)
                print(f"[DEBUG] 임베딩 생성 완료 (차원: {len(embedding)})")
                
                # PostgreSQL에 저장
                save_result = save_to_postgresql(
                    title=title,
                    content=preprocessed_content,
                    url=url,
                    original_category=original_category,
                    ai_category=ai_category,
                    keywords=keywords,
                    embedding=embedding,
                    source=source,
                    writer=writer
                )

                output_data = {
                    "title":title,
                    "content":preprocessed_content,
                    "url":url,
                    "original_category": original_category,
                    "ai_category": ai_category,
                    "keywords":keywords,
                    "embedding":embedding, 
                    "source":source,
                    "writer":writer, 
                    "publish_date":write_date

                }

                filename = f"news_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
                filepath = os.path.join("/opt/batch/data/realtime", filename)
                with open(filepath, 'w',encoding ='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False)

                print(f"JSON 파일로 저장 완료: {filepath}")
                print(f"[DEBUG] 저장 결과: {save_result}")
                return f"Successfully processed: {title}"

            else:
                print(f"[Skip] 내용 없음: {title}")
                return f"Skipped (empty content): {title}"
                
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return error_msg

def main():
    print("Flink 컨슈머 시작: 초기 설정")
    
    # 데이터베이스 연결 확인
    if not test_database_connection():
        print("❌ 데이터베이스 연결 실패. 애플리케이션을 종료합니다.")
        return
    
    print("데이터베이스 연결 성공")
    
    # Flink 실행 환경 설정
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)  # 병렬 처리 수준 설정
    
    print("Flink 환경 설정 완료")
    
    # Kafka connector JAR 등록 - 환경 변수에서 경로 가져오기
    kafka_jar = os.getenv("KAFKA_CONNECTOR_PATH", "/opt/flink/lib/flink-sql-connector-kafka-3.3.0-1.20.jar")
    
    print(f"카프카 커넥터 경로: {kafka_jar}")
    env.add_jars(f"file://{kafka_jar}")
    
    print("Kafka 커넥터 JAR 등록 완료")
    
    # Kafka Consumer 설정 - 도커 네트워크에 맞게 서버 주소 변경
    kafka_props = {
        'bootstrap.servers': 'kafka:9092',  # 도커 컨테이너 이름으로 호스트 설정
        'group.id': 'flink_news_processor',
        'auto.offset.reset': 'earliest'  # 가장 오래된 메시지부터 읽기
    }
    
    print("Kafka 속성 설정 완료")
    
    consumer = FlinkKafkaConsumer(
        topics='news',
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )
    
    # 모든 메시지 읽도록 설정
    consumer.set_start_from_earliest()
    
    print("Kafka 컨슈머 설정 완료")
    
    # Kafka에서 메시지 수신
    stream = env.add_source(consumer)
    
    print("메시지 스트림 생성")
    
    # 뉴스 데이터 처리 로직 적용
    processed_stream = stream.map(NewsProcessor())
    
    # 처리 결과 출력 (옵션)
    processed_stream.print()
    
    print("처리 스트림 설정 완료")
    
    # Flink 작업 실행
    print("Flink 작업 실행 시도...")
    try:
        env.execute("News Data Processing and Storage")
        print("Flink 작업 정상 실행")
    except Exception as e:
        print(f"Flink 작업 실행 중 오류 발생: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 