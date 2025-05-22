import os
import glob
from datetime import datetime
from airflow.providers.apache.hdfs.hooks.webhdfs import WebHDFSHook

def move_json_files(**context):
    """realtime 디렉토리에서 news_*.json 파일들을 HDFS의 news_archive 디렉토리로 이동시키는 함수"""
    source_dir = "/opt/airflow/data/realtime"
    hdfs_target_dir = "/user/news_archive"
    
    # WebHDFS 연결 설정
    webhdfs_hook = WebHDFSHook(webhdfs_conn_id="webhdfs_default")
    client = webhdfs_hook.get_conn()
    
    # DAG 실행 날짜 사용
    execution_date = context.get('ds', datetime.now().strftime("%Y-%m-%d"))
    today = execution_date.replace("-", "/")
    hdfs_date_dir = f"{hdfs_target_dir}/{today}"
    
    # HDFS 타겟 디렉토리 확인 및 생성
    if not webhdfs_hook.check_for_path(hdfs_target_dir):
        print(f"HDFS 디렉토리 {hdfs_target_dir}이 없습니다. 생성합니다.")
        client.makedirs(hdfs_target_dir)
        print(f"HDFS 디렉토리 {hdfs_target_dir}를 생성했습니다.")
    else:
        print(f"HDFS 디렉토리 {hdfs_target_dir} 존재합니다.")
    
    # 날짜별 디렉토리 생성
    if not webhdfs_hook.check_for_path(hdfs_date_dir):
        client.makedirs(hdfs_date_dir)
        print(f"HDFS 날짜 디렉토리 {hdfs_date_dir} 생성했습니다.")
    
    # 이동할 파일 패턴
    file_pattern = os.path.join(source_dir, "news_*.json")
    
    # 파일 목록 가져오기
    files = glob.glob(file_pattern)
    
    if not files:
        print(f"이동할 파일이 없습니다: {file_pattern}")
        return 0
    
    # 각 파일을 HDFS로 이동
    moved_count = 0
    for file_path in files:
        file_name = os.path.basename(file_path)
        hdfs_file_path = f"{hdfs_date_dir}/{file_name}"
        
        # WebHDFS에 파일 업로드 (client.upload 사용)
        client.upload(hdfs_file_path, file_path, overwrite=True)
        print(f"HDFS 파일 업로드 성공: {file_path} -> {hdfs_file_path}")
        
        # 원본 파일 삭제
        os.remove(file_path)
        print(f"원본 파일 삭제: {file_path}")
        
        moved_count += 1
    
    print(f"총 {moved_count}개의 파일을 HDFS로 이동했습니다.")
    return moved_count