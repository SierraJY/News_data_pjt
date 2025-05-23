#!/bin/bash

# 에어플로우와 연결해야할 커넥션이 spark와 hdfs 두 가지 있어서, 쉘스크립트로 만들어둠~~~~~~~~~~~~~~!!!!!!!!!!!!!
# 안되면 GUI로도 가능함 admin -> connection~~~~~~!!!!!!!!!!!!!!!!

# 스크립트가 실행되었는지 확인하기 위한 마커 파일
MARKER_FILE="/opt/airflow/connections_initialized"

# 이미 초기화되었는지 확인
if [ -f "$MARKER_FILE" ]; then
    echo "Airflow 커넥션이 이미 초기화되었습니다."
    exit 0
fi

echo "Airflow 커넥션 초기화 준비 중..."

# 서비스가 준비되었는지 확인
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_retries=30
    local retry_interval=10
    
    echo "$service_name 서비스 준비 확인 중... ($host:$port)"
    
    for i in $(seq 1 $max_retries); do
        if curl -s -m 1 "http://$host:$port" > /dev/null 2>&1 || curl -s -m 1 "$host:$port" > /dev/null 2>&1; then
            echo "$service_name 서비스가 준비되었습니다!"
            return 0
        fi
        echo "$i/$max_retries: $service_name 서비스 대기 중... ($host:$port)"
        sleep $retry_interval
    done
    
    echo "$service_name 서비스에 연결할 수 없습니다. 초기화를 중단합니다."
    return 1
}

# Spark 마스터 서비스 확인 (웹 UI 포트로 확인)
if ! wait_for_service spark-master 8080 "Spark"; then
    exit 1
fi

# Hadoop NameNode 서비스 확인
if ! wait_for_service namenode 9870 "Hadoop NameNode"; then
    exit 1
fi

echo "모든 서비스가 준비되었습니다. Airflow 커넥션을 설정합니다..."

# Spark 커넥션 추가
airflow connections add spark_default \
    --conn-type spark \
    --conn-host spark-master \
    --conn-port 7077 \
    --conn-extra '{"deploy-mode": "client"}'

# Hadoop 커넥션 추가
airflow connections add webhdfs_default \
    --conn-type webhdfs \
    --conn-host namenode \
    --conn-port 9870 \
    --conn-login hadoop \
    --conn-extra '{"use_ssl": false}'

# 초기화 완료 마커 생성
touch "$MARKER_FILE"
echo "Airflow 커넥션 초기화 완료!" 