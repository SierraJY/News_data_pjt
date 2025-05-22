"""
뉴스 챗봇 모듈 - LangChain 기반 RAG 구현
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 환경 변수 로드 방법 1: 컨테이너 내부 경로 사용
dotenv_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # 환경 변수 로드 방법 2: 프로젝트 루트 디렉토리 경로 설정 (최상위 디렉토리)
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
    dotenv_path = os.path.join(PROJECT_ROOT, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        print(f"경고: .env 파일을 찾을 수 없습니다. 경로 확인: {dotenv_path}")

# OpenAI API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    print(f"경고: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. 현재 디렉토리: {os.getcwd()}")
    print(f"찾는 .env 파일 경로: {dotenv_path}")
    print(f"환경 변수 목록: {os.environ.keys()}")
    # 임시 대체 로직 (실제 API 키로 대체해야 함)
    os.environ["OPENAI_API_KEY"] = "sk-..."  # 실제 API 키로 교체 필요

# 챗봇 프롬프트 템플릿 정의
CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """너는 친절한 뉴스 비서 <뉴비>야.
- 뉴스 기사 내용을 바탕으로 사용자의 질문에 쉽고 친절하게 대답해줘.
- 기사의 내용에 없는 정보는 "죄송해요, 여기 보고계신 기사에서는 찾을 수 없네요."라고 말해줘.
- 답변은 항상 한국어로 제공해줘.
- 답변은 간결하고 명확하게 해줘.

### 제목: {title}
### 작성자: {writer}
### 작성일: {write_date}
### 내용: {content}
"""),
    ("human", "{question}")
])

# LLM 모델 초기화
def get_llm():
    """OpenAI LLM 모델 인스턴스를 반환합니다."""
    try:
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    except Exception as e:
        print(f"LLM 초기화 오류: {e}")
        raise

# 단일 질문에 대한 응답 생성 함수
def get_single_response(news_data, question):
    """
    뉴스 데이터와 질문을 받아 LLM 응답을 생성합니다.
    
    Args:
        news_data (dict): 뉴스 기사 정보 (title, writer, write_date, content 포함)
        question (str): 사용자 질문
        
    Returns:
        str: LLM 응답 내용
    """
    llm = get_llm()
    chain = CHAT_PROMPT | llm
    
    response = chain.invoke({
        "title": news_data.get("title", "제목 없음"),
        "writer": news_data.get("writer", "작성자 미상"),
        "write_date": news_data.get("write_date", "날짜 정보 없음"),
        "content": news_data.get("content", "내용 없음"),
        "question": question
    })
    
    return response.content

# 세션 기반 대화 처리 함수
def process_conversation(messages, news_data, question):
    """
    기존 대화 내역과 새 질문을 처리하여 응답을 생성합니다.
    
    Args:
        messages (list): 기존 대화 메시지 목록
        news_data (dict): 뉴스 기사 정보
        question (str): 사용자 질문
        
    Returns:
        tuple: (응답 내용, 업데이트된 메시지 목록)
    """
    llm = get_llm()
    
    # 첫 질문이면 시스템 메시지 생성
    if not messages:
        system_content = f"""너는 친절한 뉴스 비서 <뉴비>야.
- 뉴스 기사 내용을 바탕으로 사용자의 질문에 쉽고 친절하게 대답해줘.
- 기사의 내용에 없는 정보는 "죄송해요, 여기 보고계신 기사에서는 찾을 수 없네요."라고 말해줘.
- 답변은 항상 한국어로 제공해줘.
- 답변은 간결하고 명확하게 해줘.

### 제목: {news_data.get('title', '제목 없음')}
### 작성자: {news_data.get('writer', '작성자 미상')}
### 작성일: {news_data.get('write_date', '날짜 정보 없음')}
### 내용: {news_data.get('content', '내용 없음')}
"""
        messages = [SystemMessage(content=system_content)]
    
    # 사용자 질문 추가
    messages.append(HumanMessage(content=question))
    
    # 컨텍스트 윈도우 관리 (최근 10개 메시지만 유지)
    if len(messages) > 20:
        # 시스템 메시지는 유지하고 나머지 중 오래된 것 제거
        system_message = messages[0] if isinstance(messages[0], SystemMessage) else None
        messages = messages[-19:]  # 최근 19개 메시지만 유지
        if system_message:
            messages = [system_message] + messages
    
    # LLM에 메시지 전달하여 응답 생성
    response = llm.invoke(messages)
    
    # 응답 메시지 추가
    messages.append(AIMessage(content=response.content))
    
    return response.content, messages

# 테스트 함수
def test_chatbot():
    """챗봇 기능을 테스트합니다."""
    test_news = {
        "title": "삼성전자, 인공지능 반도체 신규 공정 발표",
        "writer": "김기자",
        "write_date": "2025-05-22",
        "content": "삼성전자는 오늘 차세대 인공지능 반도체를 위한 신규 3나노 공정을 발표했다. 이 기술은 기존 대비 성능을 20% 향상시키고 전력 효율을 30% 개선했다. 특히 데이터 센터, 모바일 기기, 자율주행차 등 고성능 컴퓨팅 분야에서 활용이 기대된다."
    }
    
    question = "이 기술은 어떤 분야에 활용될 수 있나요?"
    response = get_single_response(test_news, question)
    print(f"질문: {question}")
    print(f"응답: {response}")
    
    # 세션 기반 대화 테스트
    messages = []
    response, messages = process_conversation(messages, test_news, question)
    print("\n세션 기반 대화 테스트:")
    print(f"질문1: {question}")
    print(f"응답1: {response}")
    
    question2 = "성능은 얼마나 향상되었나요?"
    response2, messages = process_conversation(messages, test_news, question2)
    print(f"\n질문2: {question2}")
    print(f"응답2: {response2}")

if __name__ == "__main__":
    test_chatbot() 