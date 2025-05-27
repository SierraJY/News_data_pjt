# 뉴스 데이터 통합 파이프라인: 수집-분석-리포팅-시각화 시스템

이 프로젝트는 Docker 기반 데이터 엔지니어링 환경에서 뉴스 기사 데이터를 수집, 처리, 분석하고 자동화된 리포트를 생성하는 통합 파이프라인을 구현합니다.

<div style="display: flex; justify-content: space-between;">
  <img src="README_img/flow_chart.png" style="width: 80%;">
</div>

## 목차
- [주요 특징 및 기술 스택](#주요-기술-스택)
- [데이터 파이프라인 아키텍처](#데이터-파이프라인-아키텍처)
- [기능 설명](#기능-설명)
- [프로젝트 구조](#프로젝트-구조)
- [컨테이너 구성](#컨테이너-구성)
- [env 파일 설정](#env-파일-설정)
- [Python 패키지 설정](#python-패키지-설정)
- [명령어로 직접 실행](#명령어로-직접-실행)
- [주의사항](#주의사항)

## 주요 기술 스택
<div style="margin-bottom: 10px;">
   <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=Python&logoColor=white">
   <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white">
   <img src="https://img.shields.io/badge/Apache%20Spark-E25A1C?style=flat&logo=apachespark&logoColor=white">
   <img src="https://img.shields.io/badge/Apache%20Kafka-231F20?style=flat&logo=apachekafka&logoColor=white">
   <img src="https://img.shields.io/badge/Apache%20Airflow-017CEE?style=flat&logo=apacheairflow&logoColor=white">
   <img src="https://img.shields.io/badge/Apache%20Flink-E6526F?style=flat&logo=apacheflink&logoColor=white">
   <img src="https://img.shields.io/badge/Apache%20Hadoop-66CCFF?style=flat&logo=apachehadoop&logoColor=black">
   <img src="https://img.shields.io/badge/HDFS-FF6B35?style=flat&logo=apache&logoColor=white">
   <img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white">
   <img src="https://img.shields.io/badge/Vue.js-4FC08D?style=flat&logo=vuedotjs&logoColor=white">
   <img src="https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white">
   <img src="https://img.shields.io/badge/Elasticsearch-005571?style=flat&logo=elasticsearch&logoColor=white">
</div>

## 데이터 파이프라인 아키텍처
```
[RSS Feeds] → [Kafka Producer] → [Kafka] → [Flink Consumer] 
                                                   ↓
                                           [AI Processing]
                                        (Claude API or OpenAI API Analysis)
                                                   ↓
                                    [PostgreSQL] ← → [HDFS realtime/]
                                         ↓                    ↓
                                   [Logstash]           [Spark Analysis]
                                         ↓                    ↓
                                  [Elasticsearch]      [PDF Report]
                                         ↓                    ↓
                                     [Kibana]         [Email Delivery]
                                                           ↓
                                                [HDFS news_archive/]
```

## 기능 설명
<div style="display: flex; justify-content: space-between;">
  <img src="README_img/news_list.png" style="width: 48%;">
  <img src="README_img/news_dashboard.png" style="width: 48%;">
</div>

- **뉴스 데이터 수집 (Kafka Producer)**
   - RSS 피드를 통해 여러 뉴스사의 기사 수집
   - 수집된 데이터를 Kafka 토픽으로 전송

- **웹 인터페이스 제공 (Django + Vue)**
   - 데이터베이스에 저장된 뉴스 기사를 웹 UI로 제공
   - 사용자 기능 (로그인, 회원가입)
   - 인터랙션 기능 (좋아요, 조회수 확인)
   - 기사 상세 정보 및 목록 조회

<div style="display: flex; justify-content: space-between;">
  <img src="README_img/airflow_dag.png" style="width: 48%;">
  <img src="README_img/email_reports.png" style="width: 48%;">
</div>
<br>
<div style="display: flex; justify-content: space-between;">
  <img src="README_img/report_text.png" style="width: 48%;">
  <img src="README_img/report_chart.png" style="width: 48%;">
</div>

- **데이터 처리 (Flink Consumer)**
   - Kafka 토픽에서 데이터 수신
   - Anthropic Claude API를 활용한 텍스트 분석:
     - 키워드 추출
     - 카테고리 자동 분류
     - 텍스트 임베딩 생성 (해시 기반 임베딩 사용)

- **배치 처리 (Airflow + Spark)**
   - 정기적인 데이터 분석 및 가공 작업 수행
   - 스케줄링된 워크플로우 관리
   - Spark를 활용한 대용량 데이터 처리 및 분석
   - 분석 결과 시각화 및 저장

- **일일 뉴스 리포트 생성**:
     - **HDFS 기반 완전 무파일시스템 파이프라인**:
       1. Flink → HDFS realtime 저장
       2. Spark → HDFS에서 데이터 읽어 분석
       3. PDF 리포트 생성
       4. HDFS 내부 파일 아카이브 (realtime → news_archive)
       5. 이메일 자동 발송
     - Spark 클러스터 활용 대량 뉴스 데이터 분석
     - Claude API 활용 자연어 보고서 작성
     - 데이터 시각화 그래프 자동 생성
     - PDF 리포트 생성 및 이메일 자동 발송

- **데이터 저장 (PostgreSQL)**
   - 처리된 데이터를 PostgreSQL 데이터베이스에 저장
   - pgvector 확장을 통한 벡터 데이터 저장

<div style="display: flex; justify-content: space-between;">
   <img src="README_img/hadoop_realtime.png" style="width: 48%;">
  <img src="README_img/hadoop_archive.png" style="width: 48%;">
</div>

- **분산 파일 시스템 (HDFS)**
   - Hadoop Distributed File System을 통한 대용량 데이터 저장
   - 실시간 데이터 임시 저장소 `/user/realtime/` (Flink에서 처리된 JSON 파일)
   - 영구 보관 아카이브 `/user/news_archive/YYYY/MM/DD/` (날짜별 구조화된 저장)
   - 데이터 영속성 Docker 볼륨을 통한 컨테이너 재시작 후에도 데이터 보존
   - WebHDFS API HTTP 기반 파일 시스템 접근으로 안정적인 데이터 전송

<div style="display: flex; justify-content: space-between;">
  <img src="README_img/search.png" style="width: 48%;">
  <img src="README_img/index_for_search.png" style="width: 48%;">
</div>

- **검색 기능 (Elasticsearch + Logstash)**
   - PostgreSQL 데이터를 Logstash를 통해 Elasticsearch로 이관
   - 뉴스 제목, 내용, 카테고리, 키워드 기반 전문 검색
   - 검색 결과 관련도 순 정렬
   - Django REST API를 통한 검색 엔드포인트 제공
   - Vue.js 프론트엔드에서 실시간 검색 인터페이스 제공


<div style="display: flex; justify-content: space-between;">
  <img src="README_img/kibana1.png" style="width: 48%;">
  <img src="README_img/kibana2.png" style="width: 48%;">
</div>

- **데이터 인사이트 및 시각화 (Kibana)**
   - Elasticsearch 데이터 기반 실시간 대시보드 구성
   - 뉴스 카테고리별 분포 및 트렌드 시각화
   - 키워드 빈도 분석 및 워드클라우드 제공
   - 사용자 검색 패턴 분석 및 모니터링
   - 커스텀 대시보드를 통한 뉴스 데이터 인사이트 도출


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
│   ├── vue/              # Vue 프론트엔드 서비스 설정
│   ├── spark/            # Spark 서비스 설정 (테스트 환경용)
│   ├── spark_cluster/    # Spark 클러스터 서비스 설정 (Bitnami 이미지 활용)
│   ├── airflow/          # Airflow 서비스 설정
│   └── hadoop/           # Hadoop HDFS 서비스 설정 및 초기화 스크립트
└── src/                   # 소스 코드 디렉토리
    ├── up_ingest_codes/   # 뉴스 기사 추출 함수 및 DB 직접 적재용 코드(kafka 컨테이너에서 실행)
    ├── kafka_producer/    # Kafka 프로듀서 코드 (kafka 컨테이너에서 실행)
    ├── flink_consumer/    # Flink 컨슈머 코드 및 데이터 전처리 로직 (flink 컨테이너에서 실행)
    │   └── config/        # Flink 관련 설정 파일 디렉터리
    ├── batch/             # 배치 처리 및 Airflow 관련 코드
    │   ├── dags/          # Airflow DAG 파일 및 스크립트
    │   │   └── scripts/   # DAG에서 사용하는 스크립트 파일
    │   ├── logs/          # Airflow 로그 파일
    │   ├── plugins/       # Airflow 플러그인
    │   ├── config/        # Airflow 설정 파일
    │   ├── data/          # 배치 처리용 데이터 파일
    │   └── output/        # 배치 처리 결과 출력 파일
    ├── logstash/          # Logstash 설정 및 스크립트
    │   └── data/          # Logstash 데이터 디렉토리
    └── vue_django_codes/  # 웹 애플리케이션 프론트엔드 및 백엔드 코드
        ├── news_front/    # Vue 기반 프론트엔드
        │   ├── src/       # Vue 소스 코드
        │   └── public/    # 정적 파일
        └── news_backend/  # Django 기반 백엔드
            ├── news/      # 뉴스 관련 앱 (API, 모델 등)
            ├── users/     # 사용자 관련 앱 (인증, 권한 등)
            └── news_backend/ # 프로젝트 설정
```

## 컨테이너 구성

1. **ubuntu-python**: 시스템 점검 및 테스트용 환경 (주 사용 컨테이너 아님/주석 처리)
   - up_ingest_codes: RSS를 통해 수집한 데이터를 바로 DB에 적재하는 코드
   - up_test_codes: RSS → PostgreSQL 직접 적재 테스트 코드

2. **spark**: 테스트 스파크 환경 (주 사용 컨테이너 아님/주석 처리)

3. **kafka**: 메시지 스트리밍 서비스
   - kafka_producer: RSS 수집하여 Kafka 토픽으로 전송하는 코드
   - kafka_test_codes: RSS 피드 테스트, Kafka 프로듀서/컨슈머 테스트 코드
   - article_extractors.py: 뉴스 기사 본문 추출 유틸리티 (단일 파일 마운트)
   
4. **flink**: 스트림 처리 서비스
   - flink_consumer: Kafka 스트림 데이터 처리, 전처리, DB 저장을 위한 통합 모듈
   - flink_test_codes: DB 연결 테스트, Flink 컨슈머 테스트 코드

5. **postgres**: 데이터베이스 서비스
   - 뉴스 기사 정보 저장
   - pgvector 확장을 통한 임베딩 벡터 저장
   
6. **spark_cluster**: 데이터 처리 및 분석 환경 (Bitnami 이미지)
   - spark_test_codes: Spark 관련 테스트 및 예제 코드
   - 분석 및 데이터 처리에 활용

7. **airflow**: 워크플로우 관리 및 배치 작업 스케줄링
   - batch/dags: Airflow DAG 파일 및 스크립트
   - batch/config: Airflow 설정 파일
   - batch/plugins: Airflow 플러그인
   - Spark 작업 조율 및 스케줄링
   - 주요 컴포넌트:
     - airflow-webserver: 웹 UI 제공 (8080 포트)
     - airflow-scheduler: DAG 스케줄링 및 실행
     - airflow-worker: 작업 실행 및 처리
     - flower: Celery 작업 모니터링 (5555 포트)
     - redis: Celery 메시지 브로커
     - postgres-airflow: Airflow 메타데이터 저장용 PostgreSQL 인스턴스

8. **django**: 백엔드 API 서비스
   - Django REST Framework 기반 API 제공
   - 뉴스 기사 조회, 좋아요, 조회수 기록 등 기능 제공
   - JWT 기반 사용자 인증 처리

9. **vue**: 프론트엔드 웹 서비스
   - Vue.js 기반 단일 페이지 애플리케이션(SPA)
   - 반응형 디자인으로 뉴스 기사 조회 및 인터랙션 제공
   - 사용자 로그인, 회원가입, 좋아요 기능 구현

10. **elasticsearch**: 검색 엔진 서비스
   - 뉴스 데이터 색인 및 전문 검색 기능 제공
   - 관련도 기반 검색 결과 제공
   - 분산 검색 및 분석 기능 지원

11. **logstash**: 데이터 수집 및 변환 서비스
   - PostgreSQL에서 Elasticsearch로 데이터 이관
   - 데이터 변환 및 전처리 파이프라인 제공
   - 스케줄링된 데이터 동기화 작업 수행

12. **kibana**: 데이터 시각화 및 분석 서비스
   - Elasticsearch 데이터 기반 대시보드 제공
   - 뉴스 데이터 분석 및 시각화 도구
   - 사용자 검색 패턴 및 행동 분석

## env 파일 설정

`.env` 파일에 다음 내용을 설정합니다:

```
# 데이터베이스 설정
DB_USERNAME=<사용자명>
DB_PASSWORD=<비밀번호>

# API 키
ANTHROPIC_API_KEY=<Anthropic API 키>

# Airflow 설정
AIRFLOW_UID=1000
```

## Python 패키지 설정

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
requests
```

## 명령어로 직접 실행

### 1. Docker 컨테이너 빌드 및 실행

```bash
# 도커 환경 정리
docker system prune -a
```

```bash
# 모든 서비스를 빌드하고 시작
docker compose up --build
```

### 2. 데이터 수집 및 처리 파이프라인 실행

```bash
# 카프카 컨테이너에서 프로듀서 실행
docker exec -it kafka python /opt/workspace/kafka_producer/news_producer.py

# 플링크 컨테이너에서 컨슈머 실행
docker exec -it flink python /opt/workspace/flink_consumer/flink_consumer.py
```

### 3. Airflow Spark 커넥션 설정

Airflow에서 Spark 작업을 실행하기 위한 커넥션 추가(GUI(Admin > Connections)로도 가능):
```bash
docker exec -it airflow-webserver bash -c "airflow connections add spark_default --conn-type spark --conn-host spark-master --conn-port 7077 --conn-extra '{\"deploy-mode\": \"client\"}'"
```

### 4. Airflow Hadoop 커넥션 설정
```bash
docker exec -it airflow-webserver bash -c "airflow connections add webhdfs_default --conn-type webhdfs --conn-host namenode --conn-port 9870 --conn-login hadoop --conn-extra '{\"use_ssl\": false}'"
```

### 5. 웹 인터페이스 접속

**Django 백엔드 API**
- 기본 URL: http://localhost:8000/api/
- 주요 엔드포인트:
  - 뉴스 목록: http://localhost:8000/api/news/
  - 사용자 로그인: http://localhost:8000/api/users/login/
  - 사용자 등록: http://localhost:8000/api/users/register/

**Vue 프론트엔드**
- 접속 URL: http://localhost:3000/
- 기능:
  - 뉴스 목록 조회
  - 뉴스 상세 보기
  - 로그인 및 회원가입
  - 좋아요 기능

**Airflow 웹 UI**
- 접속 URL: http://localhost:8080/
- 로그인 정보: 사용자명 `airflow`, 비밀번호 `airflow`
- 기능:
  - DAG 목록 및 실행 상태 확인
  - 작업 스케줄링 및 관리
  - 로그 확인 및 문제 해결
  - Spark 작업 모니터링
  - Variable 및 Connection 관리

**HDFS Web UI (NameNode)**
- 접속 URL: http://localhost:9870/
- 기능:
  - HDFS 파일 시스템 브라우징
  - 클러스터 상태 및 DataNode 모니터링
  - 파일 및 디렉토리 관리
  - 스토리지 사용량 확인
  - 실시간 데이터 저장소(`/user/realtime/`) 및 아카이브(`/user/news_archive/`) 조회

**Spark UI**
- 접속 URL: http://localhost:8085/
- Spark 작업의 상태 및 성능 모니터링

**Kibana**
- 접속 URL: http://localhost:5601/
- 기능:
  - Elasticsearch 데이터 탐색 및 시각화
  - 뉴스 데이터 분석 대시보드
  - 검색 패턴 및 사용자 행동 분석
  - 커스텀 시각화 및 리포트 생성


## 주의사항

- Anthropic Claude API를 사용하므로 API 키가 필요합니다
- 임베딩 생성 시 해시 기반 간단한 방식을 사용하므로, 실제 프로덕션에서는 적절한 임베딩 서비스로 대체해야 합니다
- Flink와 Kafka 연결에 필요한 JAR 파일이 올바르게 설치되어 있는지 반드시 확인해야 합니다

### Git LFS 관련 주의사항
큰 바이너리 파일(예: JAR 파일)은 Git LFS(Large File Storage)를 통해 관리됩니다. 저장소를 클론한 후에는 다음 명령어를 실행하여 LFS 파일을 가져와야 합니다:

```bash
# Git LFS 설치
sudo apt-get install git-lfs

# Git LFS 초기화 및 파일 가져오기
git lfs install
git lfs pull
```

특히 `services/flink/config/flink-sql-connector-kafka-3.3.0-1.20.jar` 파일은 Git LFS로 관리되므로, 이 파일이 필요한 Flink 서비스가 정상 작동하려면 위 명령어를 실행해야 합니다.

### Kafka 커넥터 JAR 파일이 없는 경우(Git LFS 사용 불가한 경우)
Flink에서 Kafka를 사용하려면 커넥터 JAR 파일이 필요합니다. 다음 경로에 JAR 파일을 다운로드하세요:

```
services/flink/config/flink-sql-connector-kafka-3.3.0-1.20.jar
```

Kafka 커넥터 JAR 파일은 다음 링크에서 다운로드할 수 있습니다:
- https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.20/flink-sql-connector-kafka-3.3.0-1.20.jar

### Docker 컨테이너 설정 관련 주의사항

1. **x-airflow-common 설정**
   - docker-compose.yml 파일에서 `x-airflow-common` 설정은 YAML 앵커(anchor)로서 services 섹션 밖에 위치해야 합니다.
   - 이 설정이 services 섹션 내에 위치할 경우 독립 서비스로 간주되어 오류가 발생할 수 있습니다.

2. **서비스 의존성 설정**
   - 서비스 간 의존성 설정 시 단순 시작 순서만 지정하는 것보다 `condition: service_healthy`를 사용하는 것이 좋습니다.
   - 예시:
     ```yaml
     django:
       depends_on:
         postgres:
           condition: service_healthy
     ```
   - 이렇게 설정하면 postgres 서비스가 완전히 준비된 후에만 django 서비스가 시작됩니다.

3. **데이터베이스 연결 설정**
   - 데이터베이스 연결 시 컨테이너 간 통신에는 서비스 이름(예: 'postgres')을 호스트 이름으로 사용해야 합니다.
   - 'localhost'는 컨테이너 자신을 가리키므로 다른 컨테이너의 데이터베이스에 연결할 때 사용하면 안 됩니다.
   - Django settings.py 예시:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': 'news',
             'USER': 'juyeon1',
             'PASSWORD': 'juyeon1',
             'HOST': 'postgres',  # 컨테이너 서비스 이름
             'PORT': '5432',      # 컨테이너 내부 포트
         }
     }
     ```

4. **Airflow 실행 시 주의사항**
   - Airflow는 first-time initdb 이후에 정상 실행됩니다.
   - Airflow 웹서버, 스케줄러, 워커가 모두 실행 중인지 확인해야 합니다.
   - DAG 파일은 src/batch/dags 디렉터리에 위치해야 합니다.
   - Spark과 통합 시 JAVA_HOME 환경 변수가 올바르게 설정되어 있어야 합니다 (docker-compose.yml의 x-airflow-common 설정 참조).
   - Airflow 로그는 src/batch/logs 디렉터리에서 확인할 수 있습니다.
   - 반드시 `.env` 파일에 `AIRFLOW_UID` 설정이 있어야 파일 권한 문제가 발생하지 않습니다.