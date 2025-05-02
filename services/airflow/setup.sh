#!/bin/bash
# Airflow UID 설정
if [[ ! -f .env ]]; then
  echo "Airflow UID 설정 파일 생성 중..."
  echo -e "AIRFLOW_UID=$(id -u)" > .env
  echo "AIRFLOW_UID가 $(id -u)로 설정되었습니다."
else
  echo "기존 .env 파일이 있습니다. 이 파일의 AIRFLOW_UID 설정을 사용합니다."
fi

echo "Airflow 초기화 완료!" 