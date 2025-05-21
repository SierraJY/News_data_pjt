import os
import glob
import shutil
from datetime import datetime
from airflow.providers.apache.hdfs.hooks.hdfs import HDFSHook

def move_json_files(**kwargs):
    """realtime 디렉토리에서 news_*.json 파일들을 HDFS의 news_archive 디렉토리로 이동시키는 함수"""
    source_dir = "/opt/airflow/data/realtime"
    hdfs_target_dir = "/user/news_archive"
    
    # HDFS 연결 설정
    hdfs_hook = HDFSHook(hdfs_conn_id="hdfs_default")
    
    # HDFS 타겟 디렉토리 확인 및 생성
    if not hdfs_hook.check_for_path(hdfs_target_dir):
        print(f"HDFS 디렉토리 {hdfs_target_dir}이 없습니다. 생성합니다.")
        hdfs_hook.mkdir(hdfs_target_dir)
        print(f"HDFS 디렉토리 {hdfs_target_dir}를 생성했습니다.")
    else:
        print(f"HDFS 디렉토리 {hdfs_target_dir} 존재합니다.")
    
    # 이동할 파일 패턴
    file_pattern = os.path.join(source_dir, "news_*.json")
    
    # 파일 목록 가져오기
    files = glob.glob(file_pattern)
    
    if not files:
        print(f"이동할 파일이 없습니다: {file_pattern}")
        return
    
    # 각 파일을 HDFS로 이동
    moved_count = 0
    for file_path in files:
        file_name = os.path.basename(file_path)
        
        # HDFS에 업로드할 타겟 경로 (YYYY/MM/DD 폴더 구조 사용)
        today = datetime.now().strftime("%Y/%m/%d")
        hdfs_date_dir = f"{hdfs_target_dir}/{today}"
        
        # 날짜별 디렉토리 생성
        if not hdfs_hook.check_for_path(hdfs_date_dir):
            hdfs_hook.mkdir(hdfs_date_dir)
            print(f"HDFS 날짜 디렉토리 {hdfs_date_dir} 생성했습니다.")
        
        # HDFS로 파일 업로드
        hdfs_file_path = f"{hdfs_date_dir}/{file_name}"
        
        try:
            # HDFS에 파일 업로드
            hdfs_hook.load_file(
                file_path,
                hdfs_file_path,
                overwrite=True
            )
            print(f"HDFS 파일 업로드 성공: {file_path} -> {hdfs_file_path}")
            
            # 원본 파일 삭제
            os.remove(file_path)
            print(f"원본 파일 삭제: {file_path}")
            
            moved_count += 1
        except Exception as e:
            print(f"HDFS 파일 업로드 실패: {file_path} -> {hdfs_file_path}, 오류: {e}")
    
    print(f"총 {moved_count}개의 파일을 HDFS로 이동했습니다.")