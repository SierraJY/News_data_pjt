FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 백엔드 의존성 파일 복사 및 설치
COPY ./src/vue_django_codes/news_backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 설정 스크립트 복사
COPY ./services/django/setup.sh /app/setup.sh
RUN chmod +x /app/setup.sh

# 포트 노출
EXPOSE 8000

# 시작 명령어
CMD ["bash", "-c", "chmod +x ./setup.sh && ./setup.sh && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"] 