from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from .filters import FilterUser
import django_filters.rest_framework as filters
from api_app.models import User
from api_app.serializers import UserSerializer, UserMatchSerializer


class UserCreateView(generics.CreateAPIView):
    """
    Эндпоинт создания пользователя. Метод создания - POST
    """
    serializer_class = UserSerializer


class UserListView(generics.ListAPIView):
    """
    Эндпоинт списка пользователей.
    Поддерживает фильтрацию по фамилии(last_name), имени(first_name), и полу(sex).
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FilterUser


class UserMatchView(APIView):

    def get(self, request, pk):
        user_data = UserSerializer(self.request.user)
        data = user_data.data
        data['friend'] = pk
        serializer = UserMatchSerializer(self.request.user, data=data, context={'match': False, 'pk': pk})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

