import os

# 호스트 설정
ALLOWED_HOSTS = ["*"]

# 데이터베이스 설정
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "news"),
        "USER": os.environ.get("DB_USERNAME", "juyeon1"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "juyeon1"),
        "HOST": os.environ.get("DB_HOST", "postgres"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# CORS 설정
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
    "http://vue:5173"
]

CORS_ALLOW_CREDENTIALS = True 