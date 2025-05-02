CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE news_article (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    writer VARCHAR(255) NOT NULL,
    write_date TIMESTAMP NOT NULL,
    category VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    url VARCHAR(200) UNIQUE NOT NULL,
    keywords JSON DEFAULT '[]'::json,
    embedding VECTOR(1536) NULL
);

-- auth_user 테이블은 Django의 마이그레이션으로 생성

-- news_like 및 news_view 테이블은 auth_user 테이블 생성 후 Django 마이그레이션으로 처리하거나 별도로 생성

-- 관리자 계정 추가 (Django의 createsuperuser 또는 마이그레이션 이후 수동으로 추가)

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO juyeon1;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO juyeon1;

GRANT CREATE ON SCHEMA public TO juyeon1;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO juyeon1;