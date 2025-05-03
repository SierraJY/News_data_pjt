import os
import glob
import json
from collections import defaultdict

def analyze_json_files(directory_path):
    """JSON 파일들의 구조를 분석하는 함수"""
    
    print(f"분석 대상 디렉토리: {directory_path}")
    
    # 디렉토리 존재 확인
    if not os.path.exists(directory_path):
        print(f"디렉토리가 존재하지 않습니다: {directory_path}")
        return
    
    # 디렉토리 내 모든 파일 확인
    all_files = os.listdir(directory_path)
    print(f"디렉토리 내 총 파일 수: {len(all_files)}")
    
    # 확장자별 파일 수 확인
    extensions = defaultdict(int)
    for file in all_files:
        ext = os.path.splitext(file)[1].lower()
        extensions[ext] += 1
    
    print("\n확장자별 파일 수:")
    for ext, count in extensions.items():
        if ext == '':
            print(f"  확장자 없음: {count}개")
        else:
            print(f"  {ext}: {count}개")
    
    # JSON 파일 찾기 (여러 패턴으로)
    json_patterns = ["*.json", "*.JSON", "*.Json"]
    json_files = []
    
    for pattern in json_patterns:
        found_files = glob.glob(os.path.join(directory_path, pattern))
        json_files.extend(found_files)
        print(f"\n'{pattern}' 패턴으로 찾은 파일: {len(found_files)}개")
    
    # 중복 제거
    json_files = list(set(json_files))
    print(f"\n총 JSON 파일 수: {len(json_files)}")
    
    if not json_files:
        # JSON이 아닌 파일들도 확인
        print("\nJSON 파일이 없습니다. 다른 파일들 확인:")
        for i, file in enumerate(all_files[:10]):  # 처음 10개만
            file_path = os.path.join(directory_path, file)
            print(f"\n파일 {i+1}: {file}")
            
            # 파일 크기 확인
            try:
                size = os.path.getsize(file_path)
                print(f"  크기: {size} bytes")
                
                # 텍스트 파일인 경우 처음 몇 줄 읽어보기
                if size > 0 and size < 1000000:  # 1MB 미만
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            first_line = f.readline().strip()
                            print(f"  첫 줄: {first_line[:100]}...")
                    except Exception as e:
                        print(f"  읽기 실패: {e}")
            except Exception as e:
                print(f"  크기 확인 실패: {e}")
        return
    
    # JSON 파일 분석 (이전 코드와 동일)
    field_count_stats = defaultdict(list)
    field_keys_stats = defaultdict(list)
    error_files = []
    
    for idx, file_path in enumerate(json_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                num_fields = len(data)
                field_keys = sorted(data.keys())
                field_keys_str = str(field_keys)
                
                field_count_stats[num_fields].append(file_path)
                field_keys_stats[field_keys_str].append(file_path)
                
                if idx < 3:
                    print(f"\n파일 {idx+1}: {os.path.basename(file_path)}")
                    print(f"  필드 수: {num_fields}")
                    print(f"  필드 목록: {field_keys}")
                    
        except Exception as e:
            error_files.append((file_path, str(e)))
    
    # 결과 출력
    print("\n" + "="*50)
    print("분석 결과")
    print("="*50)
    
    print("\n[필드 개수별 파일 수]")
    for num_fields, files in sorted(field_count_stats.items()):
        print(f"{num_fields}개 필드: {len(files)}개 파일")
    
    if error_files:
        print("\n[에러 발생 파일]")
        for file_path, error in error_files:
            print(f"  {os.path.basename(file_path)}: {error}")

# 실행
if __name__ == "__main__":
    # 다양한 경로 시도
    possible_paths = [
        "/opt/airflow/data/realtime",
        "./data/realtime",
        "data/realtime",
        "/opt/batch/data/realtime",
        "src/batch/data/realtime"
    ]
    
    for path in possible_paths:
        print(f"\n{'='*50}")
        print(f"경로 시도: {path}")
        print('='*50)
        
        if os.path.exists(path):
            analyze_json_files(path)
            break
        else:
            print(f"경로가 존재하지 않습니다: {path}")
    else:
        print("\n\n현재 디렉토리:", os.getcwd())
        print("현재 디렉토리의 내용:")
        for item in os.listdir('.'):
            print(f"  {item}")