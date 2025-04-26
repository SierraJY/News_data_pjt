from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import NewsViewSet, user_dashboard, record_article_view

router = DefaultRouter()
router.register(r'', NewsViewSet, basename='News')

urlpatterns = [
    path('dashboard/', user_dashboard, name='user-dashboard'),
    path('<int:pk>/view/', record_article_view, name='record-article-view'),
]

urlpatterns += router.urls