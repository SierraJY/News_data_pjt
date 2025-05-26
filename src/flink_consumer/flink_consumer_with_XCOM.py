"""
Flink 컨슈머 메인 애플리케이션
- Kafka에서 뉴스 데이터를 소비하여 처리하는 Flink 애플리케이션
- 전처리, 임베딩 생성, 키워드 추출, 데이터베이스 저장 기능
- JSON 파일을 HDFS에 직접 저장
- Kafka Producer가 생성한 메시지 개수를 받아 해당 개수만큼 처리 후 자동 종료
"""

import os
import sys
import json
import traceback
import requests
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

# 전역 변수로 처리된 메시지 개수와 예상 메시지 개수를 저장 (MapFunction이 아닌 Flink 잡 전체에서 공유)
# Flink MapFunction은 각 병렬 인스턴스마다 별도의 상태를 가질 수 있으므로,
# 실제로는 Flink의 상태 관리(State Management) 기능을 사용해야 정확하지만,
# 간단한 종료 로직을 위해 여기서는 PyFlink의 특성상 좀 더 직접적인 접근을 시도합니다.
# 하지만 MapFunction 내에서 직접 global 변수를 사용하는 것은 Flink의 병렬 처리 모델에 맞지 않으므로,
# Flink의 Source Function 또는 ProcessFunction과 같은 더 저수준의 API를 사용해야 정확한 메시지 카운팅 및 종료가 가능합니다.
# 현재 PyFlink의 FlinkKafkaConsumer와 MapFunction 조합에서는 메시지 개수 기반 종료가 직관적이지 않습니다.
#
# **중요**: PyFlink의 MapFunction에서 직접적으로 외부 상태(global processed_count)를 공유하고
# 애플리케이션을 종료시키는 것은 Flink의 설계 원칙(분산 처리, 상태 일관성)에 부합하지 않으며,
# 병렬 처리 환경에서 정확히 동작하지 않을 가능성이 매우 높습니다.
# 예를 들어, 병렬도(parallelism)가 1보다 크면 각 MapFunction 인스턴스는 자신이 처리한 메시지만 카운트합니다.
#
# 따라서 아래 코드는 개념적인 이해를 돕기 위함이며, 실제 프로덕션 환경에서는 Flink의 카운터(Counter)와
# 외부 모니터링 시스템(예: Prometheus, JMX)을 통해 메시지 처리 완료를 감지하고,
# Airflow에서 Flink Job API를 통해 취소하는 방식이 더 안정적입니다.
#
# 하지만 현재 주어진 BashOperator 및 Python 환경의 제약을 고려하여, 가장 근접한 방식으로 구현해봅니다.
# 가장 간단한 해결책은 Flink의 병렬도를 1로 설정하여 단일 스레드에서 MapFunction이 실행되도록 하는 것입니다.

processed_message_count = 0
expected_message_count = -1 # 초기값: 알 수 없음

def save_to_hdfs(data, filename):
    """WebHDFS API를 사용하여 HDFS에 JSON 파일 저장"""
    try:
        namenode_url = "http://namenode:9870"
        hdfs_path = f"/user/realtime/{filename}"

        # JSON 데이터를 문자열로 변환
        json_content = json.dumps(data, ensure_ascii=False, indent=2)

        # WebHDFS API를 사용하여 파일 업로드
        # 1단계: 업로드 URL 받기
        create_url = f"{namenode_url}/webhdfs/v1{hdfs_path}?op=CREATE&user.name=hadoop&overwrite=true"
        response = requests.put(create_url, allow_redirects=False, timeout=30)

        if response.status_code == 307:
            # 2단계: 실제 데이터 업로드
            upload_url = response.headers['Location']
            upload_response = requests.put(
                upload_url,
                data=json_content.encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                timeout=60
            )

            if upload_response.status_code == 201:
                print(f"HDFS 저장 성공: {hdfs_path}")
                return True
            else:
                print(f"HDFS 업로드 실패: {upload_response.status_code} - {upload_response.text}")
                return False
        else:
            print(f"HDFS 업로드 URL 생성 실패: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"HDFS 저장 중 오류: {e}")
        return False

class NewsProcessor(MapFunction):
    """Kafka에서 수신한 뉴스 데이터를 처리하는 맵 함수"""
    # PyFlink의 MapFunction은 상태를 직접 공유하기 어렵지만,
    # 여기서는 병렬도를 1로 설정하여 단일 인스턴스에서 실행되도록 가정합니다.
    # 프로덕션에서는 Flink의 Counter나 Broadcast State를 고려해야 합니다.

    def open(self, runtime_context):
        # MapFunction이 초기화될 때마다 호출될 수 있으므로, 전역 변수 초기화는 주의가 필요.
        # 여기서는 CLI 인자로 받은 expected_message_count를 활용할 예정.
        pass

    def map(self, message):
        global processed_message_count
        global expected_message_count

        try:
            print(f"[DEBUG] 새 메시지 수신: {message}")

            data = json.loads(message)
            print(f"[Processing] {data.get('title', 'No title')}")

            title = data.get('title', '')
            content = data.get('content', '')
            url = data.get('url', '')
            original_category = data.get('category', '')
            source = data.get('source', '')
            writer = data.get('writer', '')
            original_keywords = data.get('keywords', [])
            write_date = data.get('write_date','')

            if content:
                print(f"[DEBUG] 콘텐츠 처리 시작: {title[:50]}...")

                preprocessed_content = preprocess_content(content)
                ai_category = transform_classify_category(preprocessed_content)
                print(f"[DEBUG] AI 카테고리 분류: {ai_category}")

                if not original_keywords:
                    keywords = transform_extract_keywords(preprocessed_content)
                else:
                    keywords = original_keywords
                print(f"[DEBUG] 추출된 키워드: {keywords}")

                embedding = transform_to_embedding(preprocessed_content)
                print(f"[DEBUG] 임베딩 생성 완료 (차원: {len(embedding)})")

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
                hdfs_save_result = save_to_hdfs(output_data, filename)

                if hdfs_save_result:
                    print(f"HDFS 저장 완료: /user/realtime/{filename}")
                else:
                    print(f"HDFS 저장 실패: {filename}")

                print(f"[DEBUG] DB 저장 결과: {save_result}")

                # 메시지 처리 카운트 증가
                processed_message_count += 1
                print(f"[INFO] 현재 처리된 메시지 개수: {processed_message_count} / 예상: {expected_message_count}")

                # 예상 메시지 개수에 도달하면 애플리케이션 종료 시도
                # Flink 스트리밍 잡은 env.execute()가 블로킹 호출이므로, MapFunction 내에서 직접 종료하기 어렵습니다.
                # 다음 단계인 Airflow에서 메시지 처리 완료 여부를 판단하여 Flink 잡을 취소하는 것이 일반적입니다.
                # 하지만 현재 BashOperator의 제약을 고려하여, 여기서는 간단한 종료 로직을 넣어봅니다.
                # **이 방법은 Flink의 정확한 종료를 보장하지 않으므로 주의가 필요합니다.**
                if expected_message_count != -1 and processed_message_count >= expected_message_count:
                    print(f"[INFO] 예상 메시지 개수({expected_message_count})에 도달했습니다. Flink 애플리케이션 종료 시도...")
                    # 스트리밍 잡은 MapFunction 내에서 직접적으로 종료하는 것이 어렵습니다.
                    # sys.exit()는 전체 Python 프로세스를 종료시키지만, Flink의 자원 정리에는 문제가 있을 수 있습니다.
                    # 가장 이상적인 방법은 Flink API를 통해 잡을 취소하는 것이지만, BashOperator에서는 복잡합니다.
                    # 여기서는 일단 sys.exit()를 사용하여 프로세스를 종료하도록 합니다.
                    sys.exit(0) # 성공적인 종료를 의미
                    # return "TERMINATE" # MapFunction의 반환값으로 종료를 제어할 수는 없습니다.

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
    global expected_message_count
    print("Flink 컨슈머 시작: 초기 설정")

    # 명령줄 인자 파싱
    if len(sys.argv) > 1:
        try:
            expected_message_count = int(sys.argv[1])
            print(f"예상 처리 메시지 개수: {expected_message_count}")
        except ValueError:
            print("경고: 예상 메시지 개수가 유효한 숫자가 아닙니다. 계속 실행합니다.")
    else:
        print("경고: 예상 메시지 개수가 지정되지 않았습니다. Kafka 메시지를 무기한 대기합니다.")

    # 데이터베이스 연결 확인
    if not test_database_connection():
        print("❌ 데이터베이스 연결 실패. 애플리케이션을 종료합니다.")
        return

    print("데이터베이스 연결 성공")

    # Flink 실행 환경 설정
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)  # 병렬 처리 수준 설정: 메시지 카운트 기반 종료를 위해 1로 고정
                               # 병렬도가 1보다 크면 MapFunction 내부의 processed_message_count가
                               # 전체 메시지 개수를 정확히 반영하지 못하여 예상대로 종료되지 않을 수 있습니다.

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
        # Flink의 스트리밍 잡은 기본적으로 무한 실행됩니다.
        # sys.exit()를 통해 강제 종료되는 경우, env.execute()는 예외를 발생시키며 종료됩니다.
        env.execute("News Data Processing and Storage")
        print("Flink 작업 정상 종료 (모든 메시지 처리 완료 또는 다른 조건에 의해 종료)")
    except Exception as e:
        # sys.exit()로 인한 SystemExit 예외를 포함하여 모든 예외 처리
        if isinstance(e, SystemExit):
            print("Flink 작업이 예상 메시지 개수 도달로 인해 종료되었습니다.")
        else:
            print(f"Flink 작업 실행 중 오류 발생: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()