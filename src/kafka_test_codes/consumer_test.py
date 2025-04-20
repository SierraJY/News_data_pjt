"""
# Kafka 컨슈머 테스트 코드
#
# 테스트 실행 방법:
# 1. 먼저 Kafka 프로듀서 테스트를 실행합니다:
#    docker exec -it kafka python /opt/workspace/kafka_test_codes/rss_producer_test.py
#
# 2. 별도의 터미널에서 이 컨슈머 테스트를 실행합니다:
#    docker exec -it kafka python /opt/workspace/kafka_test_codes/consumer_test.py
#
# 테스트 완료 조건:
# - 콘솔에 "[Consumed] {'title': '예시 뉴스', 'link': 'http://example.com'}" 형태의 메시지가 출력되면 성공
# - 만약 메시지가 출력되지 않는다면, 토픽에 메시지가 없거나 Kafka가 제대로 동작하지 않는 것입니다.
# - 프로그램이 계속 대기 상태로 유지됩니다(Ctrl+C로 종료 가능).
"""

from kafka import KafkaConsumer
import json

# Kafka consumer properties
kafka_props = {
    'bootstrap_servers': 'kafka:9092',  # Docker 컨테이너 이름으로 변경
    'group_id': 'consumer_group',
    'auto_offset_reset': 'earliest',  # 처음부터 읽기
    'enable_auto_commit': True,
    'value_deserializer': lambda x: json.loads(x.decode('utf-8'))
}

# Kafka Consumer 생성
consumer = KafkaConsumer("news", **kafka_props)

# 메시지 수신
for msg in consumer:
    print(f"[Consumed] {msg.value}") 