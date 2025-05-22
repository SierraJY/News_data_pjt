import os
import json
from datetime import datetime
from airflow.providers.apache.hdfs.hooks.webhdfs import WebHDFSHook

def move_json_files(**context):
    """HDFS realtime 디렉토리에서 news_*.json 파일들을 HDFS news_archive 디렉토리로 이동시키는 함수"""
    source_hdfs_dir = "/user/realtime"
    target_hdfs_dir = "/user/news_archive"
    
    # WebHDFS 연결 설정
    webhdfs_hook = WebHDFSHook(webhdfs_conn_id="webhdfs_default")
    client = webhdfs_hook.get_conn()
    
    # DAG 실행 날짜 사용
    execution_date = context.get('ds', datetime.now().strftime("%Y-%m-%d"))
    today = execution_date.replace("-", "/")
    target_date_dir = f"{target_hdfs_dir}/{today}"
    
    print(f"HDFS 소스 디렉토리: {source_hdfs_dir}")
    print(f"HDFS 타겟 디렉토리: {target_date_dir}")
    
    # HDFS 타겟 디렉토리 확인 및 생성
    if not webhdfs_hook.check_for_path(target_hdfs_dir):
        print(f"HDFS 디렉토리 {target_hdfs_dir}이 없습니다. 생성합니다.")
        client.makedirs(target_hdfs_dir)
        print(f"HDFS 디렉토리 {target_hdfs_dir}를 생성했습니다.")
    else:
        print(f"HDFS 디렉토리 {target_hdfs_dir} 존재합니다.")
    
    # 날짜별 디렉토리 생성
    if not webhdfs_hook.check_for_path(target_date_dir):
        client.makedirs(target_date_dir)
        print(f"HDFS 날짜 디렉토리 {target_date_dir} 생성했습니다.")
    
    # HDFS source 디렉토리에서 news_*.json 파일 목록 가져오기
    try:
        file_list = client.list(source_hdfs_dir)
        news_files = [f for f in file_list if f.startswith('news_') and f.endswith('.json')]
    except Exception as e:
        print(f"HDFS 소스 디렉토리 조회 실패: {e}")
        return 0
    
    if not news_files:
        print(f"이동할 news_*.json 파일이 없습니다: {source_hdfs_dir}")
        return 0
    
    print(f"발견된 JSON 파일 수: {len(news_files)}")
    
    # 각 파일을 HDFS 내에서 이동
    moved_count = 0
    for file_name in news_files:
        source_file_path = f"{source_hdfs_dir}/{file_name}"
        target_file_path = f"{target_date_dir}/{file_name}"
        
        try:
            # HDFS 내에서 파일 이동 (copy + delete)
            # 1. 파일 내용 읽기
            with client.read(source_file_path) as reader:
                file_content = reader.read()
            
            # 2. 타겟 위치에 쓰기
            with client.write(target_file_path, overwrite=True) as writer:
                writer.write(file_content)
            
            # 3. 원본 파일 삭제
            client.delete(source_file_path)
            
            print(f"HDFS 파일 이동 성공: {source_file_path} -> {target_file_path}")
            moved_count += 1
            
        except Exception as e:
            print(f"HDFS 파일 이동 실패: {source_file_path} -> {target_file_path}, 오류: {e}")
    
    print(f"총 {moved_count}개의 파일을 HDFS 내에서 이동했습니다.")
    return moved_count