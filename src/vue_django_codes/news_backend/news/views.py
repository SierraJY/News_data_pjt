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

    @action(detail=True, methods=['post'], url_path='like')
    def like(self, request, pk=None):
        news = self.get_object()
        user = request.user
        like, created = Like.objects.get_or_create(user=user, news=news)
        if not created:
            return Response({'message': '이미 좋아요한 뉴스입니다.'}, status=400)
        return Response({'message': '좋아요 완료'})

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
