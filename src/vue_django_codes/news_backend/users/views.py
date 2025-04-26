# from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny  # 이 줄 추가
from .serializers import UserSerialzier
from django.contrib.auth.models import User 

# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerialzier
    permission_classes = [AllowAny]  # AllowAny 직접 사용