"""
PostgreSQL 데이터베이스 연결 및 조작 모듈
- 뉴스 데이터 저장 기능
- 데이터베이스 연결 관리
"""

import os
import json
import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json
from dotenv import load_dotenv
import traceback

# 환경 변수 로드
load_dotenv()

def get_db_connection():
    """
    PostgreSQL 데이터베이스 연결을 생성하는 함수
    - 도커 컨테이너 환경에 맞는 연결 설정
    """
    try:
        conn = psycopg2.connect(
            host="postgres",  # 도커 컨테이너 이름
            dbname="news",
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        traceback.print_exc()
        return None

def test_database_connection():
    """
    데이터베이스 연결 테스트 함수
    """
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(f"PostgreSQL 연결 성공: {version[0]}")
            conn.close()
            return True
        return False
    except Exception as e:
        print(f"데이터베이스 연결 테스트 오류: {e}")
        return False

def save_to_postgresql(title, content, url, original_category=None, ai_category=None, 
                        keywords=None, embedding=None, source=None, writer=None):
    """
    처리된 뉴스 데이터를 PostgreSQL에 저장하는 함수
    
    Parameters:
    - title: 뉴스 제목
    - content: 뉴스 본문 (전처리 후)
    - url: 뉴스 URL (고유 식별자)
    - original_category: 원본 카테고리
    - ai_category: AI가 분류한 카테고리
    - keywords: 추출된 키워드 리스트
    - embedding: 임베딩 벡터
    - source: 뉴스 출처 (신문사)
    - writer: 작성자
    
    Returns:
    - 성공 여부를 나타내는 불리언 값
    """
    if not title or not url:
        print("필수 데이터 누락: 제목 또는 URL")
        return False
    
    # 데이터 준비
    category = ai_category if ai_category else original_category
    if not category:
        category = "기타"
        
    if keywords and isinstance(keywords, list):
        keywords_json = json.dumps(keywords, ensure_ascii=False)
    elif keywords and isinstance(keywords, str):
        try:
            # 문자열이 JSON 형식인지 확인
            json.loads(keywords)
            keywords_json = keywords
        except:
            keywords_json = json.dumps([keywords], ensure_ascii=False)
    else:
        keywords_json = '[]'
        
    # 데이터베이스 연결
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            # 이미 존재하는 URL인지 확인
            cur.execute("SELECT id FROM news_article WHERE url = %s", (url,))
            existing_record = cur.fetchone()
            
            if existing_record:
                print(f"이미 존재하는 URL: {url}, 업데이트 수행")
                # 기존 레코드 업데이트
                update_query = """
                    UPDATE news_article 
                    SET title = %s, content = %s, category = %s, keywords = %s
                """
                params = [title, content, category, keywords_json]
                
                if embedding:
                    update_query += ", embedding = %s"
                    params.append(embedding)
                
                update_query += " WHERE url = %s"
                params.append(url)
                
                cur.execute(update_query, params)
            else:
                # 새 레코드 삽입
                insert_query = """
                    INSERT INTO news_article (title, writer, write_date, category, content, url, keywords, embedding)
                    VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s)
                """
                cur.execute(insert_query, (
                    title, 
                    writer if writer else "미상", 
                    category, 
                    content, 
                    url, 
                    keywords_json,
                    embedding
                ))
                
            conn.commit()
            print(f"✅ 저장 완료: {title}")
            return True
    except Exception as e:
        conn.rollback()
        print(f"❌ 저장 실패: {title} - {e}")
        traceback.print_exc()
        return False
    finally:
        conn.close() 