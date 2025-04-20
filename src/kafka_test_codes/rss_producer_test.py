"""
# RSS 프로듀서 테스트 코드
# 
# Docker 환경에서 실행 방법:
# docker exec -it kafka python /opt/workspace/kafka_test_codes/rss_producer_test.py
#
# 메시지 확인 방법:
# docker exec -it kafka kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic news --from-beginning
"""

from kafka import KafkaProducer
import json
import time


# Kafka 브로커 주소 (Docker 컨테이너 이름으로 변경)
KAFKA_BROKER = "kafka:9092"
# Kafka 토픽 이름
TOPIC = "news"

# Kafka Producer 생성 (value는 JSON 직렬화)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 예시 데이터 전송
sample = {"title": "예시 뉴스", "link": "http://example.com"}
producer.send(TOPIC, sample)
print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sent: {sample['title']}")
producer.flush()
producer.close()
print("Producer closed") 