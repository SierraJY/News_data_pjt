from django.shortcuts import render
from .models import News, Like, ArticleView  # ArticleView 모델 임포트 추가
from rest_framework import viewsets, permissions
from .serializers import NewsSerializer
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response 
from django.db.models import Count
from .serializers import DashboardSerializer
from rest_framework.permissions import IsAuthenticated

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