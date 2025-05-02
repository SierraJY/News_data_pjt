#!/bin/bash
# settings.py 파일이 존재하는지 확인
if [ -f /app/news_backend/settings.py ]; then
    # local_settings 임포트 코드가 있는지 확인
    if ! grep -q "local_settings" /app/news_backend/settings.py; then
        # 없으면 추가
        echo "" >> /app/news_backend/settings.py
        echo "# 로컬 설정 파일 불러오기" >> /app/news_backend/settings.py
        echo "try:" >> /app/news_backend/settings.py
        echo "    from .local_settings import *" >> /app/news_backend/settings.py
        echo "except ImportError:" >> /app/news_backend/settings.py
        echo "    pass" >> /app/news_backend/settings.py
        echo "local_settings.py 임포트 코드가 settings.py에 추가되었습니다."
    else
        echo "local_settings.py 임포트 코드가 이미 존재합니다."
    fi
else
    echo "settings.py 파일을 찾을 수 없습니다."
    exit 1
fi 