from django.shortcuts import render
from .models import News, Like, ArticleView
from rest_framework import viewsets, permissions
from .serializers import NewsSerializer
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Avg
from .serializers import DashboardSerializer
from rest_framework.permissions import IsAuthenticated
from pgvector.django import CosineDistance
from django.db.models import F
from .serializers import RecommendNewsSerializer
from elasticsearch import Elasticsearch
import os
from django.conf import settings
from django.http import HttpResponse
from gtts import gTTS
import io
import requests

# Elasticsearch 클라이언트 설정
es = Elasticsearch(["http://es01:9200"])



# Create your views here.
class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def get_permissions(self):
        if self.action == 'like':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_view_name(self):
        return "News"

    def get_queryset(self):
        return News.objects.annotate(like_count=Count('like')).only(
            'id', 'title', 'writer', 'write_date', 'category', 'content', 'url'
        )

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Elasticsearch를 사용하여 뉴스를 검색합니다.
        query 파라미터로 검색어를 받습니다.
        """
        query = request.query_params.get('query', '')
        
        if not query:
            return Response({"error": "검색어를 입력해주세요."}, status=400)
            
        try:
            # Elasticsearch 검색 쿼리 구성
            search_query = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "content^2", "category", "keywords"],
                        "fuzziness": "AUTO"
                    }
                },
                "size": 50  # 최대 50개 결과 반환
            }
            
            # Elasticsearch 검색 실행
            search_results = es.search(index="news", body=search_query)
            
            # 검색 결과에서 ID 추출
            news_ids = [int(hit["_id"]) for hit in search_results["hits"]["hits"]]
            
            if not news_ids:
                return Response({"results": [], "count": 0})
                
            # 추출한 ID로 Django ORM에서 뉴스 데이터 가져오기
            # 검색 결과의 순서를 유지하기 위해 Case/When 사용
            from django.db.models import Case, When
            preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(news_ids)])
            news_results = News.objects.filter(id__in=news_ids).order_by(preserved_order)
            
            # 시리얼라이저로 결과 변환
            serializer = self.get_serializer(news_results, many=True)
            
            return Response({
                "results": serializer.data,
                "count": len(serializer.data)
            })
            
        except Exception as e:
            return Response({"error": f"검색 중 오류가 발생했습니다: {str(e)}"}, status=500)
        
    # mattermost를 통해서 기사 공유하기 
    @action(detail=True, methods=['post'], url_path = 'share-mattermost')
    def share_to_mattermost(self, request, pk = None):
        """뉴스를 Mattermost로 공유하는 API"""
        try:
            news= self.get_object()
            webhook_url = settings.MATTERMOST_WEBHOOK_URL

            # Mattermost 메시지 포맷 
            message = {
                "text" : "### 뉴스 공유\n" + 
                f"**{news.title}**\n\n" + 
                f"카테고리 : {news.category}\n" + 
                f"작성자: {news.writer}\n" + 
                f"작성일: {news.write_date}\n\n" + 
                f"원문 링크 : {news.url}\n" + 
                f"상세 페이지: {settings.FRONTEND_URL}/news/{news.id}"
            }
            # Mattermost로 메세지 전송 
            response = requests.post(webhook_url, json=message)
            response.raise_for_status() # 예외 발생시 

            return Response({'message': 'Mattermost로 뉴스가 공유되었습니다.'})
        except Exception as e:
            return Response({'error': f"공유 중 오류가 발생했습니다: {str(e)}"}, status = 500)

    @action(detail=True, methods=['post'], url_path='like')
    def like(self, request, pk=None):
        news = self.get_object()
        user = request.user
        like, created = Like.objects.get_or_create(user=user, news=news)
        if not created:
            return Response({'message': '이미 좋아요한 뉴스입니다.'}, status=400)
        return Response({'message': '좋아요 완료'})
    @action(detail = True, methods=['post'], url_path='tts')
    def text_to_speech(self, request, pk=None):
        """
        뉴스 내용을 음성으로 변환합니다.
        """
        try:
            news=  self.get_object()
            text = news.content
            if not text:
                return Response({'error': '변환할 텍스트가 없습니다.'}, status = 400)
            tts = gTTS(text = text, lang = 'ko')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)

            response = HttpResponse(fp.read(), content_type = 'audio/mpeg')
            response['Content-Disposition'] = 'attachment; filename = news_speech.mp3'
            return response
        except Exception as e:
            return Response({'error': f'음성 변환 중 오류가 발생했습니다: {str(e)}'}, status = 500)

    @action(detail=True, methods=['post'], url_path='unlike')
    def unlike(self, request, pk=None):
        news = self.get_object()
        user = request.user
        try:
            like = Like.objects.get(user=user, news=news)
            like.delete()
            return Response({'message': '좋아요가 취소되었습니다.'})
        except Like.DoesNotExist:
            return Response({'message': '좋아요하지 않은 뉴스입니다.'}, status=400)

    @action(detail=True, methods=['get'], url_path='check-like')
    def check_like(self, request, pk=None):
        news = self.get_object()
        user = request.user
        liked = Like.objects.filter(user=user, news=news).exists()
        return Response({'liked': liked})

    @action(detail=True, methods=['get'], url_path='related')
    def get_related_news(self, request, pk=None):
        news = self.get_object()

        related_news = News.objects.exclude(id=news.id) \
            .annotate(like_count=Count('like')) \
            .only('id', 'title', 'writer', 'write_date', 'category', 'url', 'embedding') \
            .order_by(CosineDistance('embedding', news.embedding))[:5]

        serializer = self.get_serializer(related_news, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='recommend')
    def get_recommended_news(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({'error': '로그인이 필요한 서비스입니다.'}, status=401)

        try:
            liked_news_qs = News.objects.filter(like__user=user, embedding__isnull=False)

            if not liked_news_qs.exists():
                return Response({'error': '추천을 위한 좋아요 데이터가 부족합니다. 먼저 몇 개의 기사에 좋아요를 눌러주세요.'}, status=400)

            embedding_avg = liked_news_qs.aggregate(avg_embedding=Avg('embedding'))['avg_embedding']

            if embedding_avg is None:
                return Response({'error': '추천 시스템에 필요한 임베딩 데이터가 없습니다.'}, status=500)

            liked_ids = liked_news_qs.values_list('id', flat=True)

            recommended_news_qs = News.objects.exclude(id__in=liked_ids) \
                .filter(embedding__isnull=False) \
                .annotate(
                    like_count=Count('like'),
                    distance=CosineDistance('embedding', embedding_avg)
                ) \
                .defer('embedding', 'keywords') \
                .order_by('distance')[:20]

            # 별도 Serializer 사용
            serializer = RecommendNewsSerializer(recommended_news_qs, many=True)
            return Response(serializer.data)

        except Exception as e:
            print(f"추천 시스템 오류: {str(e)}")
            return Response({'error': f'추천 시스템 처리 중 오류가 발생했습니다: {str(e)}'}, status=500)
        


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    serializer = DashboardSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_article_view(request, pk):
    try:
        news = News.objects.get(pk=pk)
        ArticleView.objects.create(user=request.user, news=news)
        return Response({'message': '조회 기록이 저장되었습니다.'})
    except News.DoesNotExist:
        return Response({'error': '기사를 찾을 수 없습니다.'}, status=404)
