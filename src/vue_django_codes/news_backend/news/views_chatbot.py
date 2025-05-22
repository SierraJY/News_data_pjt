"""
뉴스 챗봇 API 뷰
"""

import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import News
from .chatbot import process_conversation

class ChatbotView(APIView):
    """
    뉴스 기사에 대한 질문을 처리하는 챗봇 API 뷰
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        사용자 질문을 처리하고 챗봇 응답을 반환합니다.
        
        요청 본문:
        - article_id: 뉴스 기사 ID
        - question: 사용자 질문
        
        응답:
        - response: 챗봇 응답
        """
        # 요청 데이터 검증
        article_id = request.data.get("article_id")
        question = request.data.get("question")
        
        if not article_id or not question:
            return Response(
                {"error": "기사 ID와 질문이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 뉴스 기사 조회
        try:
            article = get_object_or_404(News, id=article_id)
        except Exception as e:
            return Response(
                {"error": f"기사를 찾을 수 없습니다: {str(e)}"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 세션에서 대화 내역 가져오기
        session_key = f"chat_history_{request.user.id}_{article_id}"
        messages = request.session.get(session_key, [])
        
        # 메시지가 문자열로 저장된 경우 처리 (세션 직렬화 문제)
        if isinstance(messages, str):
            try:
                messages = json.loads(messages)
            except:
                messages = []
        
        # 뉴스 데이터 준비
        news_data = {
            "title": article.title,
            "writer": article.writer,
            "write_date": article.write_date.strftime("%Y-%m-%d"),
            "content": article.content
        }
        
        try:
            # 대화 처리
            response_text, updated_messages = process_conversation(messages, news_data, question)
            
            # 세션에 대화 내역 저장
            request.session[session_key] = updated_messages
            request.session.modified = True
            
            # 응답 반환
            return Response({
                "response": response_text,
                "article_id": article_id
            })
        except Exception as e:
            return Response(
                {"error": f"챗봇 응답 생성 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ChatbotResetView(APIView):
    """
    특정 기사에 대한 챗봇 대화 내역을 초기화하는 API 뷰
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, article_id):
        """
        특정 기사에 대한 대화 내역을 초기화합니다.
        
        URL 파라미터:
        - article_id: 뉴스 기사 ID
        
        응답:
        - message: 초기화 결과 메시지
        """
        session_key = f"chat_history_{request.user.id}_{article_id}"
        
        if session_key in request.session:
            del request.session[session_key]
            request.session.modified = True
            
        return Response({"message": "대화가 초기화되었습니다."}) 