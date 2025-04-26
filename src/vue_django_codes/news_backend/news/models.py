from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class News(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length = 200)
    writer = models.CharField(max_length = 255)
    write_date = models.DateTimeField()
    category = models.CharField(max_length = 50)
    content = models.TextField()
    url = models.CharField(max_length = 200)
    keywords = models.TextField(null = True, blank = True)
    embedding = models.TextField(null = True, blank = True)
    class Meta:
        db_table = 'news_article'
        managed = False # django가 이 테이블을 관리하지 않도록 설정 
        verbose_name = 'News'
        verbose_name_plural = 'News' #복수형도 News로 고정 
    def __str__(self):
        return f"[{self.write_date}] {self.title} - {self.writer}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column  = 'user_id')
    news = models.ForeignKey('News',on_delete = models.CASCADE, db_column = 'news_id')
    created_at = models.DateTimeField(auto_now_add = True)
    class Meta: 
        db_table = 'news_like'
        # managed= False
        unique_together = ('user','news') # 중복 좋아요 방지 

# ArticleView 모델 추가 - 사용자가 본 기사 추적
class ArticleView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    news = models.ForeignKey('News', on_delete=models.CASCADE, db_column='news_id')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'news_view'
        # managed = False
        unique_together = ('user', 'news', 'viewed_at')  # 동일 사용자가 같은 기사를 여러 번 볼 수 있음
