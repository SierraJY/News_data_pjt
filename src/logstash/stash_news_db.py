"""
뉴스 데이터 Elasticsearch 조회 스크립트
PostgreSQL에서 Logstash를 통해 Elasticsearch로 저장된 뉴스 데이터를 조회합니다.
"""

from elasticsearch import Elasticsearch

# Elasticsearch 클라이언트 연결 (로컬 환경에서 실행)
es = Elasticsearch("http://localhost:9200")

# 뉴스 데이터 조회 (match_all 쿼리로 모든 데이터 가져오기)
response = es.search(
    index="news",
    body={
        "query": {
            "match_all": {}
        },
        "size": 10  # 조회할 문서 수 제한
    }
)

# 결과 출력
print(f"총 {response['hits']['total']['value']}개의 뉴스 데이터가 있습니다.")
print("\n===== 뉴스 데이터 샘플 =====")
for hit in response["hits"]["hits"]:
    doc = hit['_source']
    print(f"ID: {hit['_id']}")
    print(f"제목: {doc.get('title', '제목 없음')}")
    print(f"카테고리: {doc.get('category', '카테고리 없음')}")
    
    # 키워드 출력 (배열 형태로 가정)
    keywords = doc.get('keywords', [])
    if keywords:
        print(f"키워드: {', '.join(keywords)}")
    else:
        print("키워드: 없음")
    
    # 내용 일부 출력
    content = doc.get('content', '내용 없음')
    print(f"내용 미리보기: {content[:100]}..." if len(content) > 100 else f"내용: {content}")
    print("-" * 50)
