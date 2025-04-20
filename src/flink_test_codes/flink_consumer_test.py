"""
# Flink Kafka 컨슈머 테스트 코드
#
# 테스트 실행 방법:
# 1. 먼저 Flink Kafka 컨슈머 테스트를 실행하여 데이터 수신 대기 상태로 만듭니다:
#    docker exec -it flink python /opt/workspace/flink_test_codes/flink_consumer_test.py
#
# 2. 다른 터미널에서 Kafka 프로듀서 테스트를 실행하여 메시지를 전송합니다:
#    docker exec -it kafka python /opt/workspace/kafka_test_codes/rss_producer_test.py
#
# 3. 다시 1번 단계를 실행한 터미널로 돌아가 Flink에서 메시지를 수신했는지 확인합니다.
#    메시지가 콘솔에 출력되면 테스트가 성공적으로 완료된 것입니다.
#
# 테스트 완료 조건:
# - 콘솔에 Kafka에서 수신한 메시지가 출력되면 성공
# - JAR 파일 로드, Kafka 연결, 데이터 스트림 처리 작업이 모두 정상 동작해야 함
# - 테스트는 실행 후 작업이 완료되면 자동 종료됨
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors import FlinkKafkaConsumer
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

env = StreamExecutionEnvironment.get_execution_environment()

# Kafka connector JAR 등록
kafka_connector_path = os.getenv("KAFKA_CONNECTOR_PATH")
print(f"Kafka connector path: {kafka_connector_path}")  # 경로 확인용 출력

# 경로가 존재하는지 확인
if not os.path.exists(kafka_connector_path):
    raise FileNotFoundError(f"JAR 파일을 찾을 수 없습니다: {kafka_connector_path}")
else:
    print(f"JAR 파일 확인 완료: {kafka_connector_path}")

env.add_jars(f"file://{kafka_connector_path}")
print("JAR 파일이 성공적으로 로드되었습니다.")

# Kafka Consumer 설정 (Docker 컨테이너 이름으로 변경)
kafka_props = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'flink_consumer_group'
}

consumer = FlinkKafkaConsumer(
    topics='news',
    deserialization_schema=SimpleStringSchema(),
    properties=kafka_props
)

print("Kafka 연결 설정이 완료되었습니다. 데이터 수신 대기 중...")

# Kafka에서 메시지 수신
stream = env.add_source(consumer)

stream.print()
print("Flink 작업이 시작됩니다. 메시지가 수신되면 콘솔에 출력됩니다.")

env.execute("Flink Kafka Consumer Job") 