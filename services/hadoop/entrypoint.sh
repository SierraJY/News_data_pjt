#!/bin/bash

# 원래 namenode 시작
hdfs namenode &
NAMENODE_PID=$!

# namenode가 준비될 때까지 대기
echo "Waiting for namenode to be ready..."
sleep 30

# HDFS 디렉토리 및 권한 설정
echo "Setting up HDFS directories..."
hdfs dfs -mkdir -p /user/default/news_archive
hdfs dfs -mkdir -p /user/airflow
hdfs dfs -chmod 755 /user/default
hdfs dfs -chmod 755 /user/default/news_archive
hdfs dfs -chmod 755 /user/airflow
hdfs dfs -chown default:default /user/default/news_archive

echo "HDFS setup completed!"
hdfs dfs -ls /user/

# namenode 프로세스를 포그라운드로 유지
wait $NAMENODE_PID