import os
import feedparser
import psycopg2
import json
from dotenv import load_dotenv
from datetime import datetime

# 크롤링 함수 임포트
from article_extractors import (
    extract_khan_article_body,
    extract_yna_article_body,
    extract_mk_article_body,
)

load_dotenv()

# PostgreSQL 연결
conn = psycopg2.connect(
    host="postgres",
    dbname="news",
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()
print(f"접속 유저 확인: {os.getenv('DB_USERNAME')}")

# RSS 피드 URL 목록
RSS_FEED_URLS = [
    ("khan","경제", "https://www.khan.co.kr/rss/rssdata/economy_news.xml"),
    ("khan","정치", "https://www.khan.co.kr/rss/rssdata/economy_news.xml"),
    ("khan", "사회", "https://www.khan.co.kr/rss/rssdata/society_news.xml"),
    ("mk","경제","https://www.mk.co.kr/rss/30100041/"),
    ("mk","정치","https://www.mk.co.kr/rss/30200030/"),
    ("mk","사회","https://www.mk.co.kr/rss/50400012/"),
    ("yna","경제","https://www.yna.co.kr/rss/economy.xml"),
    ("yna","정치", "https://www.yna.co.kr/rss/politics.xml"),
    ("yna", "사회","https://www.yna.co.kr/rss/society.xml")
]

def main():
    for source, category, rss_url in RSS_FEED_URLS:
        feed = feedparser.parse(rss_url)

        for entry in feed.entries:
            title = entry.title
            writer = entry.author.split()[0] if entry.get("author") else "미상"
            write_date = datetime(*entry.updated_parsed[:6])
            category = category
            url = entry.link
            keywords = json.dumps([entry.tags[0]["term"]]) if entry.get("tags") else "[]"

            if source == "khan":
                content = extract_khan_article_body(url)
            elif source == "yna":
                content = extract_yna_article_body(url)
            elif source == "mk":
                content = extract_mk_article_body(url)
            else:
                content = ""

            try:
                cur.execute("""
                    INSERT INTO news_article (title, writer, write_date, category, content, url, keywords)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING;
                """, (title, writer, write_date, category, content, url, keywords))
                conn.commit()
                print(f"✅ 삽입 완료: {title}")
            except Exception as e:
                conn.rollback()
                print(f"❌ 삽입 실패: {title} - {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
