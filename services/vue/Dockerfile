FROM node:18-slim

# 작업 디렉토리 설정
WORKDIR /app

# 프론트엔드 의존성 설치를 위한 파일 복사
COPY ./src/vue_django_codes/news_front/package*.json ./

# 의존성 설치
RUN npm install

# 환경 변수 설정
ENV VITE_BASE_URL="http://django:8000"
ENV PATH /app/node_modules/.bin:$PATH

# 포트 노출
EXPOSE 5173

# 시작 명령어
CMD ["sh", "-c", "npm run dev -- --host 0.0.0.0"] 