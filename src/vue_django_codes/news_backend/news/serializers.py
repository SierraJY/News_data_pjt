from rest_framework import serializers
from .models import News, Like, ArticleView
from django.db.models import Count
from django.contrib.auth.models import User
from collections import Counter
import json

class NewsSerializer(serializers.ModelSerializer):
     # 어노테이션 필드 명시적 추가
    like_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = News
        fields = '__all__'

class DashboardSerializer(serializers.Serializer):
    """대시보드 데이터를 위한 시리얼라이저"""
    category_stats = serializers.SerializerMethodField()
    keyword_stats = serializers.SerializerMethodField()
    weekly_views = serializers.SerializerMethodField()
    liked_articles = serializers.SerializerMethodField()
    
    def get_category_stats(self, user):
        """사용자가 본 기사의 카테고리 통계"""
        viewed_news = ArticleView.objects.filter(user=user).values_list('news_id', flat=True)
        categories = News.objects.filter(id__in=viewed_news).values_list('category', flat=True)
        
        # 카테고리별 기사 수 계산
        counter = Counter(categories)
        return [{"name": cat, "count": count} for cat, count in counter.most_common()]
        
    def get_keyword_stats(self, user):
        """사용자가 본 기사의 키워드 통계"""
        viewed_news = ArticleView.objects.filter(user=user).values_list('news_id', flat=True)
        news_with_keywords = News.objects.filter(id__in=viewed_news)
        
        # 모든 키워드 수집 및 빈도수 계산
        keywords_counter = Counter()
        for news in news_with_keywords:
            if news.keywords:
                try:
                    # 이미 리스트인 경우
                    if isinstance(news.keywords, list):
                        keywords = news.keywords
                    # JSON 문자열인 경우
                    elif isinstance(news.keywords, str):
                        try:
                            # JSON 형식으로 파싱 시도
                            keywords = json.loads(news.keywords.replace("'", "\""))
                        except:
                            # 쉼표로 구분된 문자열인 경우
                            keywords = [k.strip() for k in news.keywords.strip('[]').split(',')]
                    else:
                        # 다른 타입인 경우는 건너뜀
                        continue
                    
                    keywords_counter.update(keywords)
                except Exception as e:
                    print(f"키워드 처리 오류: {e}, 타입: {type(news.keywords)}")
                    continue
        
        # 상위 8개 키워드 반환 (10개에서 8개로 변경)
        return [{"keyword": kw, "count": count} for kw, count in keywords_counter.most_common(8)]
    
    def get_weekly_views(self, user):
        """최근 7일간 일별 조회수"""
        from datetime import datetime, timedelta
        
        # 최근 7일 데이터 가져오기
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # 날짜별로 그룹화
        views = ArticleView.objects.filter(
            user=user, 
            viewed_at__range=(start_date, end_date)
        ).extra({
            'day': "DATE(viewed_at)"
        }).values('day').annotate(count=Count('id')).order_by('day')
        
        # 결과 포맷팅
        result = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            count = 0
            for view in views:
                if str(view['day']) == date_str:
                    count = view['count']
                    break
            
            # 요일 이름으로 변환
            day_name = current_date.strftime('%A')
            result.append({
                "date": date_str,
                "day": day_name,
                "count": count
            })
            current_date += timedelta(days=1)
            
        return result
    
    def get_liked_articles(self, user):
        """사용자가 좋아요한 기사 목록"""
        liked_news_ids = Like.objects.filter(user=user).values_list('news_id', flat=True)
        liked_news = News.objects.filter(id__in=liked_news_ids)
        
        # NewsSerializer 대신 직접 필요한 필드만 반환
        return [{
            'id': news.id,
            'title': news.title,
            'writer': news.writer,
            'write_date': news.write_date,
            'category': news.category,
            'url': news.url,
            'like_count': Like.objects.filter(news=news).count()
        } for news in liked_news]


class RecommendNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            'id', 'title', 'writer', 'write_date',
            'category', 'url', 'content', 'keywords'
        ]