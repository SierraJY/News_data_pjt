#!/bin/bash

# 볼륨 디렉토리 권한 설정
echo "Setting up volume permissions..."
mkdir -p /tmp/hadoop-root/dfs/name
chown hadoop:hadoop /tmp/hadoop-root/dfs/name
chmod 755 /tmp/hadoop-root/dfs/name

# namenode format (필요한 경우에만)
if [ ! -d "/tmp/hadoop-root/dfs/name/current" ]; then
    echo "Formatting namenode..."
    hdfs namenode -format -force
fi

# namenode 백그라운드에서 시작
echo "Starting namenode..."
hdfs namenode &
NAMENODE_PID=$!

# namenode가 시작될 때까지 대기
echo "Waiting for namenode to be ready..."
sleep 30

# HDFS 디렉토리 및 권한 설정
echo "Setting up HDFS directories..."
hdfs dfs -mkdir -p /user 2>/dev/null || true
hdfs dfs -chmod 755 /user 2>/dev/null || true
hdfs dfs -chown hadoop:supergroup /user 2>/dev/null || true
hdfs dfs -mkdir -p /user/default/news_archive 2>/dev/null || true
hdfs dfs -mkdir -p /user/airflow 2>/dev/null || true
hdfs dfs -chmod 755 /user/default 2>/dev/null || true
hdfs dfs -chmod 755 /user/default/news_archive 2>/dev/null || true
hdfs dfs -chmod 755 /user/airflow 2>/dev/null || true
hdfs dfs -chown hadoop:supergroup /user/default 2>/dev/null || true
hdfs dfs -chown hadoop:supergroup /user/default/news_archive 2>/dev/null || true

echo "HDFS setup completed!"

# namenode 프로세스를 포그라운드로 유지
wait $NAMENODE_PID