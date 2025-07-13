#!/bin/bash

echo "[WAIT] Flink JobManager 준비 중..."
sleep 10

echo "[RUN] Flink Python Job 제출 중..."

# JobManager 주소를 명시적으로 지정
flink run -m jobmanager:8081 -py /opt/workspace/flink_consumer/flink_consumer.py

echo "[DONE] Flink Job 제출 완료!"
exit 0 