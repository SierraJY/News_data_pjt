"""
뉴스 챗봇 뷰 - RAG 기반 뉴스 질의응답 API
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import News
from .chatbot import process_conversation

class ChatbotView(APIView):
    """
    뉴스 챗봇 API - 세션 기반 대화 처리
    
    POST /api/news/chatbot/
    Body:
    {
        "article_id": 기사ID,
        "question": "사용자 질문"
    }
    
    Response:
    {
        "response": "AI 응답",
        "status": "success"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # 요청 데이터 파싱
            article_id = request.data.get('article_id')
            question = request.data.get('question')
            
            print(f"받은 요청: article_id={article_id}, question={question}")
            
            if not article_id or not question:
                return Response({
                    'error': '기사 ID와 질문이 모두 필요합니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 뉴스 기사 조회
            try:
                news = get_object_or_404(News, id=article_id)
                print(f"뉴스 조회 성공: {news.title}")
            except News.DoesNotExist:
                return Response({
                    'error': '해당 기사를 찾을 수 없습니다.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 뉴스 데이터 준비
            news_data = {
                'title': news.title,
                'writer': news.writer,
                'write_date': news.write_date.strftime('%Y-%m-%d') if news.write_date else '날짜 정보 없음',
                'content': news.content
            }
            
            # 세션에서 기존 대화 기록 가져오기 (딕셔너리 형태)
            session_key = f'chatbot_messages_{article_id}'
            existing_messages = request.session.get(session_key, [])
            
            print(f"기존 메시지 개수: {len(existing_messages)}")
            print(f"기존 메시지 타입: {type(existing_messages)}")
            
            # 대화 처리 (직렬화된 메시지 사용)
            response_content, updated_messages = process_conversation(
                existing_messages, 
                news_data, 
                question
            )
            
            print(f"업데이트된 메시지 개수: {len(updated_messages)}")
            print(f"메시지 샘플: {updated_messages[-1] if updated_messages else 'None'}")
            
            # 업데이트된 대화 기록을 세션에 저장 (딕셔너리 형태)
            request.session[session_key] = updated_messages
            request.session.modified = True
            
            print("세션 저장 완료")
            
            return Response({
                'response': response_content,
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # 상세한 오류 로깅
            import traceback
            print(f"챗봇 처리 중 오류 발생: {str(e)}")
            print(f"오류 상세: {traceback.format_exc()}")
            
            return Response({
                'error': f'서버 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatbotResetView(APIView):
    """
    특정 기사의 챗봇 대화 기록 초기화
    
    POST /api/news/chatbot/reset/{article_id}/
    
    Response:
    {
        "message": "대화 기록이 초기화되었습니다.",
        "status": "success"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, article_id):
        try:
            # 세션에서 해당 기사의 대화 기록 삭제
            session_key = f'chatbot_messages_{article_id}'
            if session_key in request.session:
                del request.session[session_key]
                request.session.modified = True
            
            return Response({
                'message': '대화 기록이 초기화되었습니다.',
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"대화 초기화 중 오류 발생: {str(e)}")
            return Response({
                'error': f'초기화 중 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)