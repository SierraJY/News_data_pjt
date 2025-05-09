from django.shortcuts import render
from .models import News, Like, ArticleView  # ArticleView 모델 임포트 추가
from rest_framework import viewsets, permissions
from .serializers import NewsSerializer
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response 
from django.db.models import Count, Avg
from .serializers import DashboardSerializer
from rest_framework.permissions import IsAuthenticated
from pgvector.django import CosineDistance
from django.db.models import F
from django.db import connection

# Create your views here.
class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get_permissions(self):
        if self.action == 'like':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    def get_view_name(self):
        return "News" # 직접 표시할 이름 지정 
    def get_queryset(self):
        return News.objects.annotate(like_count=Count('like')).only('id','title','writer','write_date','category', 'content','url')
    
    @action(detail=True, methods=['post'], url_path='like')
    def like(self, request, pk=None):
        news = self.get_object()
        user = request.user
        like, created = Like.objects.get_or_create(user=user, news=news)
        if not created:
            return Response({'message':'이미 좋아요한 뉴스입니다.'}, status=400)
        return Response({'message':'좋아요 완료'})
    
    @action(detail=True, methods=['get'], url_path='check-like')
    def check_like(self, request, pk=None):
        """사용자가 특정 뉴스에 좋아요를 눌렀는지 확인"""
        news = self.get_object()
        user = request.user
        liked = Like.objects.filter(user=user, news=news).exists()
        return Response({'liked': liked})
    
    @action(detail=True, methods=['get'], url_path='related')
    def get_related_news(self, request, pk=None):
        """벡터 유사도 기반으로 관련 기사 검색"""
        news = self.get_object()
        
        # CosineDistance를 사용한 코사인 유사도 검색
        # 현재 기사를 제외하고 유사도 순으로 정렬
        related_news = News.objects.exclude(id=news.id) \
                .annotate(like_count=Count('like')) \
                .only('id', 'title', 'writer', 'write_date', 'category', 'url', 'embedding') \
                .order_by(CosineDistance('embedding', news.embedding))[:5]
        
        serializer = self.get_serializer(related_news, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='recommend')
    def get_recommended_news(self, request):
        """사용자의 좋아요 기반 코사인 유사도 추천 기사 API"""
        user = request.user

        if not request.user.is_authenticated:
            return Response({'error': '로그인이 필요한 서비스입니다.'}, status=401)

        try:
            liked_news = News.objects.filter(like__user=user)

            if not liked_news.exists():
                return Response({'error': '추천을 위한 좋아요 데이터가 부족합니다. 먼저 몇 개의 기사에 좋아요를 눌러주세요.'}, status=400)

            reference_news = None
            for news in liked_news:
                if news.embedding is not None:
                    reference_news = news
                    break

            if reference_news is None:
                return Response({'error': '추천 시스템에 필요한 임베딩 데이터가 없습니다.'}, status=500)

            liked_news_ids = liked_news.values_list('id', flat=True)

            # values → annotate → order_by 순서
            recommended_news_dict = News.objects.exclude(id__in=liked_news_ids) \
                .values('id', 'title', 'writer', 'write_date', 'category', 'url', 'content') \
                .annotate(like_count=Count('like'),
                        distance=CosineDistance('embedding', reference_news.embedding)) \
                .order_by('distance')[:20]
                
            # 최신순 API와 같은 형식으로 일관성 유지
            recommended_news = []
            for item in recommended_news_dict:
                # 필요 없는 distance 필드 제거
                if 'distance' in item:
                    del item['distance']
                recommended_news.append(item)

            if not recommended_news:
                return Response({'error': '추천할 수 있는 뉴스가 없습니다.'}, status=404)

            # 최신순 API와 동일한 형식으로 반환
            return Response(recommended_news)

        except Exception as e:
            print(f"추천 시스템 오류: {str(e)}")
            return Response({'error': f'추천 시스템 처리 중 오류가 발생했습니다: {str(e)}'}, status=500)


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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    """사용자 대시보드 데이터 API"""
    serializer = DashboardSerializer(request.user)
    return Response(serializer.data)

# 기사 조회 시 조회 기록 추가 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_article_view(request, pk):
    """사용자의 기사 조회 기록"""
    try:
        news = News.objects.get(pk=pk)
        ArticleView.objects.create(user=request.user, news=news)
        return Response({'message': '조회 기록이 저장되었습니다.'})
    except News.DoesNotExist:
        return Response({'error': '기사를 찾을 수 없습니다.'}, status=404)