# 뉴스 데이터 수집 및 처리 파이프라인

이 프로젝트는 Docker 기반 데이터 엔지니어링 환경(News_DE_pjt)에서 뉴스 기사 데이터를 수집, 처리, 저장하는 파이프라인을 구현합니다.

## 실행 흐름

1. **수집 단계**: Kafka Producer가 RSS 피드에서 뉴스 데이터를 수집하고 BeautifulSoup으로 기사 본문을 추출하여 Kafka 토픽으로 전송
2. **처리 단계**: Flink Consumer가 Kafka 토픽에서 데이터를 소비하고 Anthropic Claude API를 사용하여 텍스트 분석(카테고리 분류, 키워드 추출, 임베딩 생성)
3. **저장 단계**: 처리된 데이터는 PostgreSQL에 저장되며, 임베딩 벡터는 pgvector 확장을 통해 벡터 형식으로 저장
4. **시각화 단계**: Django와 Vue.js를 통해 데이터를 웹 인터페이스로 제공하고 사용자와 상호작용
5. **확인 단계**: 웹 인터페이스 또는 PostgreSQL 쿼리를 통해 저장된 데이터 확인 및 활용

## 주요 특징 및 기술 스택

- **Docker**: 모든 서비스를 컨테이너화하여 환경 일관성 유지
- **Kafka**: 뉴스 데이터 스트리밍을 위한 메시지 브로커
- **Flink**: 실시간 스트림 처리 엔진으로 데이터 처리 및 변환
- **PostgreSQL + pgvector**: 관계형 데이터베이스와 벡터 검색 기능
- **Anthropic Claude API**: 텍스트 분석 및 처리(카테고리 분류, 키워드 추출)
- **Django + DRF**: REST API 백엔드 및 데이터 모델링
- **Vue.js**: 사용자 인터페이스 및 프론트엔드 구현
- **JWT**: 토큰 기반 사용자 인증
- **Python**: 크롤링, 데이터 처리, API 연동 등의 주요 로직 구현 언어
- **BeautifulSoup**: 웹 크롤링과 HTML 파싱을 위한 라이브러리

## 프로젝트 구조

```
./ (루트 디렉토리)
├── docker-compose.yml     # 도커 구성 파일
├── requirements.txt       # 필요한 파이썬 패키지 목록
├── .env                   # 환경 변수 설정 파일
├── services/              # 각 서비스별 도커 설정 파일
│   ├── ubuntu-python/    # Ubuntu Python 서비스 설정 (테스트 환경용)
│   ├── kafka/            # Kafka 서비스 설정
│   ├── flink/            # Flink 서비스 설정
│   ├── postgres/         # PostgreSQL 서비스 설정
│   ├── django/           # Django 백엔드 서비스 설정
│   └── vue/              # Vue 프론트엔드 서비스 설정
└── src/                   # 소스 코드 디렉토리
    ├── up_ingest_codes/   # 뉴스 기사 추출 함수 및 DB 직접 적재용 코드 (ubuntu-python 전용)
    │   ├── article_extractors.py  # 여러 뉴스 사이트에서 본문 크롤링하는 함수 모음
    │   └── news_ingest.py         # RSS 피드로 뉴스 수집 및 DB에 직접 저장하는 스크립트
    ├── up_test_codes/     # RSS->PostgreSQL 직접 적재 테스트 코드 (ubuntu-python 전용)
    │   ├── db_test.py            # DB 연결 테스트
    │   └── rss_test.py           # RSS 피드 파싱 테스트
    ├── kafka_producer/    # Kafka 프로듀서 코드 (kafka 컨테이너에서 실행)
    │   └── news_producer.py      # RSS 피드 수집 및 Kafka 토픽으로 메시지 전송
    ├── kafka_test_codes/  # Kafka 테스트 코드 (RSS 테스트, 프로듀서/컨슈머 테스트)
    │   ├── consumer_test.py      # Kafka 컨슈머 테스트 
    │   ├── rss_producer_test.py  # Kafka 프로듀서 간단 테스트
    │   └── rss_test.py           # RSS 피드 파싱 테스트
    ├── flink_consumer/    # Flink 컨슈머 코드 및 데이터 전처리 로직 (flink 컨테이너에서 실행)
    │   ├── flink_consumer.py   # Flink 스트림 처리 메인 코드
    │   ├── preprocess.py       # Anthropic Claude API 활용 텍스트 분석 및 전처리 코드
    │   ├── db_handler.py       # PostgreSQL 데이터베이스 접근 및 저장 코드
    │   └── config/             # Flink 관련 설정 파일 디렉터리
    ├── spark_test_codes/       # Spark 테스트 코드 (spark 컨테이너에서 사용)
    │   ├── data/               # Spark 테스트용 데이터 파일
    │   └── src/                # Spark 예제 및 테스트 코드
    │       └── ... (기타 Spark 예제 코드)
    ├── flink_test_codes/       # Flink 테스트 코드 (DB 테스트, Flink 컨슈머 테스트)
    │   ├── db_test.py          # 데이터베이스 연결 테스트
    │   ├── flink_consumer_test.py  # Flink Kafka 컨슈머 연결 테스트
    │   └── test1.py            # 기타 Flink 기능 테스트
    └── vue_django_codes/       # 웹 애플리케이션 프론트엔드 및 백엔드 코드
        ├── news_front/         # Vue 기반 프론트엔드
        │   ├── src/            # Vue 소스 코드
        │   ├── public/         # 정적 파일
        │   └── package.json    # 의존성 설정
        └── news_backend/       # Django 기반 백엔드
            ├── news/           # 뉴스 관련 앱 (API, 모델 등)
            ├── users/          # 사용자 관련 앱 (인증, 권한 등)
            └── news_backend/   # 프로젝트 설정
```

## 컨테이너 구성

1. **ubuntu-python**: 시스템 점검 및 테스트용 환경 (주 사용 컨테이너 아님)
   - up_ingest_codes: RSS를 통해 수집한 데이터를 바로 DB에 적재하는 코드
   - up_test_codes: RSS → PostgreSQL 직접 적재 테스트 코드
   
2. **kafka**: 메시지 스트리밍 서비스
   - kafka_producer: RSS 수집하여 Kafka 토픽으로 전송하는 코드
   - kafka_test_codes: RSS 피드 테스트, Kafka 프로듀서/컨슈머 테스트 코드
   - article_extractors.py: 뉴스 기사 본문 추출 유틸리티 (단일 파일 마운트)
   
3. **flink**: 스트림 처리 서비스
   - flink_consumer: Kafka 스트림 데이터 처리, 전처리, DB 저장을 위한 통합 모듈
   - flink_test_codes: DB 연결 테스트, Flink 컨슈머 테스트 코드

4. **postgres**: 데이터베이스 서비스
   - 뉴스 기사 정보 저장
   - pgvector 확장을 통한 임베딩 벡터 저장
   
5. **spark**: 데이터 처리 및 분석 환경 (테스트 및 개발용)
   - spark_test_codes: Spark 관련 테스트 및 예제 코드

6. **django**: 백엔드 API 서비스
   - Django REST Framework 기반 API 제공
   - 뉴스 기사 조회, 좋아요, 조회수 기록 등 기능 제공
   - JWT 기반 사용자 인증 처리

7. **vue**: 프론트엔드 웹 서비스
   - Vue.js 기반 단일 페이지 애플리케이션(SPA)
   - 반응형 디자인으로 뉴스 기사 조회 및 인터랙션 제공
   - 사용자 로그인, 회원가입, 좋아요 기능 구현

## 기능 설명

1. **뉴스 데이터 수집 (Kafka Producer)**
   - RSS 피드를 통해 여러 뉴스사의 기사 수집
   - 수집된 데이터를 Kafka 토픽으로 전송

2. **데이터 처리 (Flink Consumer)**
   - Kafka 토픽에서 데이터 수신
   - Anthropic Claude API를 활용한 텍스트 분석:
     - 키워드 추출
     - 카테고리 자동 분류
     - 텍스트 임베딩 생성 (해시 기반 임베딩 사용)

3. **데이터 저장 (PostgreSQL)**
   - 처리된 데이터를 PostgreSQL 데이터베이스에 저장
   - pgvector 확장을 통한 벡터 데이터 저장

4. **웹 인터페이스 제공 (Django + Vue)**
   - 데이터베이스에 저장된 뉴스 기사를 웹 UI로 제공
   - 사용자 기능 (로그인, 회원가입)
   - 인터랙션 기능 (좋아요, 조회수 확인)
   - 기사 상세 정보 및 목록 조회

## 설치 및 환경 설정

### 1. Kafka 커넥터 JAR 파일 설정
Flink에서 Kafka를 사용하려면 커넥터 JAR 파일이 필요합니다. 다음 경로에 JAR 파일을 다운로드하세요:

```
services/flink/config/flink-sql-connector-kafka-3.3.0-1.20.jar
```

Kafka 커넥터 JAR 파일은 다음 링크에서 다운로드할 수 있습니다:
- https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.20/flink-sql-connector-kafka-3.3.0-1.20.jar

### 2. Anthropic Claude API 및 기타 설정

Anthropic Claude API를 사용하려면 API 키가 필요합니다. Anthropic 웹사이트(https://www.anthropic.com/)에서 API 키를 발급받을 수 있습니다.

`.env` 파일에 다음 내용을 설정합니다:

```
# 데이터베이스 설정
DB_USERNAME=<사용자명>
DB_PASSWORD=<비밀번호>

# API 키
ANTHROPIC_API_KEY=<Anthropic API 키>

# Django 설정
DJANGO_SECRET_KEY=<Django 시크릿 키>
JWT_SECRET_KEY=<JWT 시크릿 키>

# 기타 설정
DEBUG=True  # 개발 환경에서만 True로 설정
```

### 3. Python 패키지 설정

필요한 Python 패키지는 프로젝트 루트 디렉토리의 `requirements.txt`에 정의되어 있습니다. 모든 컨테이너는 도커 빌드 시 이 파일을 사용하여 필요한 패키지를 설치합니다.

```bash
# requirements.txt 파일 확인
cat requirements.txt
```

프로젝트의 주요 의존성:
```
feedparser==6.0.11
kafka-python==2.0.2
numpy==1.24.3
apache-flink==1.20.0
beautifulsoup4==4.13.3
pydantic==2.10.6
psycopg2-binary==2.9.10
anthropic==0.7.0
python-dotenv==1.0.1
pyspark==3.5.4
matplotlib==3.10.0
hdfs==2.7.3
elasticsearch==8.17.1
```

## 실행 방법

### 1. Docker 컨테이너 빌드 및 실행

```bash
# 모든 서비스를 빌드하고 시작
docker compose up --build
```

### 2. 데이터 수집 및 처리 파이프라인 실행

**방법 1: Kafka-Flink 파이프라인 (권장)**
```bash
# 카프카 컨테이너에서 프로듀서 실행
docker exec -it kafka python /opt/workspace/kafka_producer/news_producer.py

# 플링크 컨테이너에서 컨슈머 실행
docker exec -it flink python /opt/workspace/flink_consumer/flink_consumer.py
```

### 3. 웹 인터페이스 접속

**Django 백엔드 API**
- 기본 URL: http://localhost:8000/api/
- 주요 엔드포인트:
  - 뉴스 목록: http://localhost:8000/api/news/
  - 사용자 로그인: http://localhost:8000/api/users/login/
  - 사용자 등록: http://localhost:8000/api/users/register/

**Vue 프론트엔드**
- 접속 URL: http://localhost:8080/
- 기능:
  - 뉴스 목록 조회
  - 뉴스 상세 보기
  - 로그인 및 회원가입
  - 좋아요 기능

### 4. 데이터 확인

PostgreSQL 데이터베이스에 접속하여 저장된 데이터를 확인합니다:

```bash
docker exec -it postgres psql -U ${DB_USERNAME} -d news
```

```sql
SELECT id, title, category, writer FROM news_article LIMIT 10;
```

### 5. 테스트 코드 실행

각 컨테이너에는 기능 테스트를 위한 코드가 포함되어 있습니다:

**Ubuntu Python 테스트 코드**
```bash
# RSS 피드 및 DB 직접 적재 테스트
docker exec -it ubuntu_python python /opt/workspace/up_test_codes/rss_test.py
docker exec -it ubuntu_python python /opt/workspace/up_test_codes/db_test.py
```

**Kafka 테스트 코드**
```bash
# RSS 피드 테스트
docker exec -it kafka python /opt/workspace/kafka_test_codes/rss_test.py

# Kafka 프로듀서 테스트
docker exec -it kafka python /opt/workspace/kafka_test_codes/rss_producer_test.py

# Kafka 컨슈머 테스트 (별도 터미널에서 실행)
docker exec -it kafka python /opt/workspace/kafka_test_codes/consumer_test.py
```

**Flink 테스트 코드**
```bash
# 데이터베이스 연결 테스트
docker exec -it flink python /opt/workspace/flink_test_codes/db_test.py

# Flink Kafka 컨슈머 테스트
docker exec -it flink python /opt/workspace/flink_test_codes/flink_consumer_test.py
```

## 주의사항

- Anthropic Claude API를 사용하므로 API 키가 필요합니다
- 임베딩 생성 시 해시 기반 간단한 방식을 사용하므로, 실제 프로덕션에서는 적절한 임베딩 서비스로 대체해야 합니다
- Flink와 Kafka 연결에 필요한 JAR 파일이 올바르게 설치되어 있는지 반드시 확인해야 합니다
- 대용량 처리 시 리소스 사용량에 주의해야 합니다

## 데이터베이스 구조

프로젝트는 다음과 같은 주요 테이블을 사용합니다:

1. **news_article**: 수집된 뉴스 기사 정보를 저장
   - `id`: 기사 ID (기본 키)
   - `title`: 기사 제목
   - `writer`: 작성자 정보
   - `write_date`: 작성 날짜
   - `category`: 기사 카테고리
   - `content`: 기사 본문
   - `url`: 원본 기사 URL
   - `keywords`: 추출된 키워드 (JSON 형식)
   - `embedding`: 텍스트 임베딩 벡터 (VECTOR 타입)

2. **auth_user**: Django의 사용자 인증 시스템에 사용되는 기본 사용자 테이블

3. **news_like**: 사용자가 좋아요 표시한 기사 정보
   - `id`: 좋아요 ID (기본 키)
   - `user_id`: 사용자 ID (외래 키)
   - `news_id`: 기사 ID (외래 키)
   - `created_at`: 좋아요 생성 시간

4. **news_view**: 사용자의 기사 조회 기록
   - `id`: 조회 ID (기본 키)
   - `user_id`: 사용자 ID (외래 키)
   - `news_id`: 기사 ID (외래 키)
   - `viewed_at`: 조회 시간

테이블 간의 관계:
- `news_like`와 `news_view`는 `news_article`의 `id`를 외래 키로 참조
- `news_like`와 `news_view`는 `auth_user`의 `id`를 외래 키로 참조