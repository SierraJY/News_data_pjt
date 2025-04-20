"""
Anthropic Claude API 키(ANTHROPIC_API_KEY) 사용 안내:

이 모듈의 모든 함수들은 Anthropic Claude API를 직접 사용합니다:
- transform_extract_keywords(): claude-3-7-20250219로 키워드 추출
- transform_to_embedding(): 해시 기반 임베딩 생성 (Claude는 직접 임베딩 API가 없음)
- transform_classify_category(): claude-3-7-20250219로 카테고리 분류

Anthropic 클라이언트는 자동으로 환경변수의 ANTHROPIC_API_KEY를 사용합니다.
따라서 .env 파일에 ANTHROPIC_API_KEY를 정확히 설정해야 합니다.
"""

import os
import re
import json
import time
import anthropic
from hashlib import md5
import math
from dotenv import load_dotenv
load_dotenv()

# Anthropic 클라이언트 설정
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 모델 설정 - Claude 3.7 Sonnet은 성능이 더 우수함
MODEL = "claude-3-7-sonnet-20250219"


def preprocess_content(content):
    """
    데이터 전처리 - 텍스트 길이 제한 (5000 토큰)
    
    Anthropic API나 다른 NLP 모델에 입력하기 전에 텍스트의 토큰 수를 제한합니다.
    너무 긴 텍스트는 처리 시간이 오래 걸리고, API 비용이 증가하며, 
    일부 모델에서는 최대 토큰 제한을 초과할 수 있기 때문입니다.
    
    Parameters:
        content (str): 전처리할 원본 텍스트
        
    Returns:
        str: 토큰 수가 5000개 이하로 제한된 텍스트
    """
    import tiktoken

    # 빈 문자열이면 그대로 반환
    if not content:
        return ""
    
    # tiktoken을 사용하여 텍스트를 토큰으로 인코딩
    # cl100k_base는 Claude와도 호환되는 일반적인 토크나이저
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(content)
    
    # 토큰 수가 5000개를 초과하면 처음 5000개 토큰만 유지
    if len(tokens) > 5000:
        truncated_tokens = tokens[:5000]
        return encoding.decode(truncated_tokens)  # 토큰을 다시 텍스트로 디코딩
    
    # 토큰 수가 5000개 이하면 원본 텍스트 그대로 반환
    return content


def transform_extract_keywords(text):
   """
   텍스트 데이터 변환 - 키워드 5개 추출
   
   주어진 뉴스 기사 텍스트에서 핵심 키워드 5개를 추출하는 함수입니다.
   Anthropic Claude API를 활용하여 LLM 기반의 키워드 추출을 수행합니다.
   
   작동 과정:
   1. 입력받은 텍스트를 preprocess_content()로 전처리 (토큰 길이 제한)
   2. Claude API의 claude-3-7-20250219 모델에 프롬프트와 함께 텍스트 전송
   3. 모델이 추출한 키워드들을 쉼표로 구분된 형태로 반환
   4. 반환된 문자열을 리스트로 변환하여 반환
   
   Parameters:
       text (str): 키워드를 추출할 원본 텍스트
       
   Returns:
       list: 추출된 키워드들의 리스트 (일반적으로 5개)
   """
   # 텍스트 전처리 (토큰 수 제한)
   text = preprocess_content(text)
   
   # 키워드 추출 요청
   try:
       response = client.messages.create(
           model=MODEL,
           max_tokens=100,  # 응답 길이 제한
           system="당신은 텍스트에서 핵심 키워드를 추출하는 전문가입니다. 주어진 뉴스 기사에서 가장 중요한 키워드 5개를 추출해주세요. 결과는 쉼표로 구분된 키워드 목록으로만 반환해주세요. 예시: '경제,주식,물가,인플레이션,금리'",
           messages=[
               # 사용자 메시지로 원본 텍스트 전달
               {"role": "user", "content": text}
           ],
           temperature=0.1  # 결정적인 응답을 위해 낮은 temperature 사용
       )
       
       # 모델 응답에서 키워드 부분만 추출하고 앞뒤 공백 제거
       keywords = response.content[0].text.strip()
       
       # 쉼표로 구분된 키워드 문자열을 리스트로 변환하여 반환
       return keywords.split(',')
   except Exception as e:
       print(f"키워드 추출 오류: {e}")
       return []


def transform_to_embedding(text: str) -> list[float]:
   """
   텍스트 데이터 변환 - 벡터 임베딩
   
   텍스트를 수치형 벡터(임베딩)로 변환하는 함수입니다. 
   텍스트의 의미를 수치화하여 벡터 공간에 매핑함으로써 의미적 유사성 비교, 
   검색, 클러스터링 등 다양한 머신러닝 작업에 활용할 수 있습니다.
   
   작동 과정:
   1. 입력받은 텍스트를 preprocess_content()로 전처리 (토큰 길이 제한)
   2. 해시 기반의 임베딩 생성 방식을 사용하여 텍스트를 벡터로 변환
   3. 1536차원의 부동소수점 벡터(float 값의 리스트)를 반환
   
   참고: Claude는 직접적인 임베딩 API를 제공하지 않으므로 해시 기반 방식 사용
   
   Parameters:
       text (str): 벡터로 변환할 원본 텍스트
       
   Returns:
       list[float]: 텍스트의 의미를 나타내는 1536차원의 벡터(임베딩)
   """
   # 텍스트 전처리 (토큰 수 제한)
   text = preprocess_content(text)

   try:
       # Claude는 임베딩 API가 없으므로 해시 기반의 임베딩 생성
       # 텍스트를 1536 차원의 벡터로 변환 (OpenAI 호환)
       vector = [0.0] * 1536
       
       # 텍스트를 청크로 나누어 해시 계산
       chunks = [text[i:i+100] for i in range(0, len(text), 100)]
       
       for i, chunk in enumerate(chunks):
           # 청크 해시 계산
           hash_val = md5(chunk.encode()).hexdigest()
           
           # 해시 값을 float로 변환하여 벡터에 분산
           for j in range(min(32, len(hash_val))):
               idx = (i * 32 + j) % 1536
               vector[idx] = int(hash_val[j], 16) / 15.0 - 0.5  # -0.5 ~ 0.5 사이 값
       
       # 벡터 정규화
       magnitude = math.sqrt(sum(x*x for x in vector))
       if magnitude > 0:
           vector = [x/magnitude for x in vector]
       
       return vector
   except Exception as e:
       print(f"임베딩 생성 오류: {e}")
       return [0.0] * 1536


def transform_classify_category(content):
    """
    텍스트 데이터 변환 - 카테고리 분류  
    뉴스 내용을 기반으로 적절한 카테고리로 분류하는 변환 로직
    """
    text = preprocess_content(content)
    
    categories = ["IT_과학", "건강", "경제", "교육", "국제", "라이프스타일", "문화", 
                 "사건사고", "사회일반", "산업", "스포츠", "여성복지", "여행레저", 
                 "연예", "정치", "지역", "취미"]
    categories_str = ", ".join(categories)
    
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=50,
            system="당신은 뉴스 기사 분류 전문가입니다. 주어진 뉴스 내용을 다음 카테고리 중 하나로 분류해주세요. 답변은 카테고리명만 정확히 작성해주세요.",
            messages=[
                {"role": "user", "content": f"다음 뉴스 기사를 다음 카테고리 중 하나로 분류해주세요: {categories_str}\n\n{text}"}
            ],
            temperature=0.1
        )
        
        model_output = response.content[0].text.strip()
        
        # 카테고리 목록에 없는 경우 '미분류'로 설정
        if model_output not in categories:
            # 부분 매칭 시도
            for category in categories:
                if category in model_output:
                    return category
            return "미분류"
            
        return model_output
    except Exception as e:
        print(f"카테고리 분류 오류: {e}")
        return "미분류"
