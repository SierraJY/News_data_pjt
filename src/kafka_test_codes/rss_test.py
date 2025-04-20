"""
# RSS 피드 테스트 코드 (Kafka 컨테이너용)
#
# 테스트 실행 방법:
# docker exec -it kafka python /opt/workspace/kafka_test_codes/rss_test.py
#
# 테스트 완료 조건:
# - 첫 번째 기사 정보가 출력되고 피드 길이가 표시되면 성공
"""

import feedparser
import requests
from bs4 import BeautifulSoup

# RSS 피드 URL (예: Khan 뉴스 RSS)
RSS_FEED_URL = "https://www.khan.co.kr/rss/rssdata/total_news.xml"

def main():
    feed = feedparser.parse(RSS_FEED_URL)
    print(feed['entries'][0])
    print(len(feed))
    

if __name__ == "__main__":
    main()
