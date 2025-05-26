from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import NewsViewSet, user_dashboard, record_article_view
from .views_chatbot import ChatbotView, ChatbotResetView

router = DefaultRouter()
router.register(r'', NewsViewSet, basename='News')

urlpatterns = [
    path('dashboard/', user_dashboard, name='user-dashboard'),
    path('<int:pk>/view/', record_article_view, name='record-article-view'),
    
    # 챗봇 API 엔드포인트
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
    path('chatbot/reset/<int:article_id>/', ChatbotResetView.as_view(), name='chatbot-reset'),
]

urlpatterns += router.urls