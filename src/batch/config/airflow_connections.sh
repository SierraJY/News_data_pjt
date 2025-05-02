#!/bin/bash

# Airflow 서버가 완전히 시작될 때까지 대기
echo "Airflow 서버가 시작될 때까지 대기 중..."
sleep 30

# Spark 연결 설정
echo "Spark 연결 설정 중..."
airflow connections add 'spark_default' \
    --conn-type 'spark' \
    --conn-host 'spark-master' \
    --conn-port '7077' \
    --conn-extra '{"queue": "default", "deploy-mode": "client"}'

echo "연결 설정이 완료되었습니다." 