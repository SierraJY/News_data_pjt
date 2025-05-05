import os
import glob
import shutil

def move_json_files(**kwargs):
    """realtime 디렉토리에서 news_*.json 파일들을 news_archive 디렉토리로 이동시키는 함수"""
    source_dir = "/opt/airflow/data/realtime"
    target_dir = "/opt/airflow/data/news_archive"
    
    # 타겟 디렉토리가 없으면 생성
    os.makedirs(target_dir, exist_ok=True)
    
    # 이동할 파일 패턴
    file_pattern = os.path.join(source_dir, "news_*.json")
    
    # 파일 목록 가져오기
    files = glob.glob(file_pattern)
    
    if not files:
        print(f"이동할 파일이 없습니다: {file_pattern}")
        return
    
    # 각 파일을 타겟 디렉토리로 이동
    moved_count = 0
    for file_path in files:
        file_name = os.path.basename(file_path)
        target_path = os.path.join(target_dir, file_name)
        
        try:
            shutil.move(file_path, target_path)
            moved_count += 1
            print(f"파일 이동 성공: {file_path} -> {target_path}")
        except Exception as e:
            print(f"파일 이동 실패: {file_path} -> {target_path}, 오류: {e}")
    
    print(f"총 {moved_count}개의 파일을 이동했습니다.")