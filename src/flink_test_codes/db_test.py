"""
# Flink 데이터베이스 연결 테스트 코드
#
# 테스트 실행 방법:
# docker exec -it flink python /opt/workspace/flink_test_codes/db_test.py
#
# 테스트 완료 조건:
# - PostgreSQL 데이터베이스에서 뉴스 기사 데이터가 출력되면 성공
# - 만약 오류가 발생하거나 데이터가 출력되지 않는다면, 데이터베이스 연결 문제 또는 테이블에 데이터가 없는 경우
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        host='postgres',
        dbname='news',
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD")
    )
    print("PostgreSQL 데이터베이스 연결 성공!")
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM news_article LIMIT 10")
    rows = cur.fetchall()
    
    if len(rows) > 0:
        print(f"\n총 {len(rows)}개의 뉴스 기사를 가져왔습니다:")
        for r in rows:
            print(r)
        print("\n데이터베이스 테스트가 성공적으로 완료되었습니다.")
    else:
        print("테이블에 데이터가 없습니다. 먼저 데이터를 적재해 주세요.")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"데이터베이스 연결 오류: {e}") 