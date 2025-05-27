"""
# Kafka Producer for News Collection
# 뉴스 RSS 피드를 크롤링하여 Kafka 토픽으로 전송하는 프로듀서
#
# 실행 방법:
# docker exec -it kafka python /opt/workspace/kafka_producer/news_producer.py
#
# 테스트 완료 조건:
# - "✅[kafka] [시간] 전송 완료: 뉴스제목" 메시지가 여러 개 표시되면 성공
# - 최종적으로 "모든 메시지 전송 완료" 및 "Producer 종료" 메시지가 출력됨
# 
# 결과 확인 방법:
# docker exec -it kafka kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic news --from-beginning
"""

import os
import sys
import json
import time
import feedparser
from kafka import KafkaProducer
from datetime import datetime
from dotenv import load_dotenv
import traceback

# 현재 경로 추가 - 도커 컨테이너 환경에 맞게 조정
sys.path.append('/opt/workspace')

# 기존 크롤링 함수 임포트
from article_extractors import (
    extract_khan_article_body,
    extract_yna_article_body,
    extract_mk_article_body
)

# 환경 변수 로드
load_dotenv()

# Kafka 설정 - 도커 컨테이너 이름으로 호스트 설정
KAFKA_BROKER = "kafka:9092"
TOPIC = "news"

# Kafka Producer 생성
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False, default=str).encode('utf-8')
)

# RSS 피드 URL 목록
RSS_FEED_URLS = [
    ("khan","경제", "https://www.khan.co.kr/rss/rssdata/economy_news.xml"),  # 경향신문
    # ("khan","정치", "https://www.khan.co.kr/rss/rssdata/economy_news.xml"),
    # ("khan", "사회", "https://www.khan.co.kr/rss/rssdata/society_news.xml"),
    # ("mk","경제","https://www.mk.co.kr/rss/30100041/"),
    # ("mk","정치","https://www.mk.co.kr/rss/30200030/"),
    # ("mk","사회","https://www.mk.co.kr/rss/50400012/"),
    # ("yna","경제","https://www.yna.co.kr/rss/economy.xml"),
    # ("yna","정치", "https://www.yna.co.kr/rss/politics.xml"),
    # ("yna", "사회","https://www.yna.co.kr/rss/society.xml")
]

def main():
    try:
        print("RSS 뉴스 데이터를 Kafka로 전송 중...")
        
        for source, category, rss_url in RSS_FEED_URLS:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {source} {category} 피드 처리 중...")
            feed = feedparser.parse(rss_url)

            for entry in feed.entries:
                # 기본 정보 추출
                title = entry.title
                writer = entry.author.split()[0] if entry.get("author") else "미상"
                write_date = datetime(*entry.updated_parsed[:6]) if entry.get("updated_parsed") else datetime.now()
                url = entry.link

                # 본문 내용 크롤링
                if source == "khan":
                    content = extract_khan_article_body(url)
                elif source == "yna":
                    content = extract_yna_article_body(url)
                elif source == "mk":
                    content = extract_mk_article_body(url)
                else:
                    content = ""

                # Kafka로 전송할 메시지 구성
                message = {
                    "source": source,
                    "title": title,
                    "writer": writer,
                    "write_date": str(write_date),
                    "category": category,
                    "content": content,
                    "url": url,
                    "timestamp": str(datetime.now())
                }

                # Kafka로 메시지 전송
                producer.send(TOPIC, message)
                print(f"✅[kafka] [{time.strftime('%Y-%m-%d %H:%M:%S')}] 전송 완료: {title}")

        # 종료 메시지 전송
        end_message = {
            "source": "SYSTEM",
            "title": "END",
            "writer": "SYSTEM",
            "write_date": str(datetime.now()),
            "category": "SYSTEM",
            "content": "END",
            "url": "",
            "timestamp": str(datetime.now())
        }
        producer.send(TOPIC, end_message)
        
        # 모든 메시지가 전송될 때까지 대기 (일반 메시지와 END 메시지 모두)
        producer.flush()
        print("모든 메시지 전송 완료 (종료 메시지 포함)")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        traceback.print_exc()
    finally:
        producer.close()
        print("Producer 종료")

if __name__ == "__main__":
    main()