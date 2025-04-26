from django.contrib import admin
from .models import News, Like
# Register your models here.
admin.site.register(News)
admin.site.register(Like)
admin.site.site_header = "뉴스 백오피스"
admin.site.site_title = "News Admin"
admin.site.index_title = "뉴스 데이터 관리 페이지"