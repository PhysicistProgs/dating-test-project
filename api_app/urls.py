from django.urls import path
from api_app import views

app_name = 'api'

urlpatterns = [
    path('clients/create/', views.UserCreateView.as_view()),
    path('list/', views.UserListView.as_view()),
    path('clients/<int:pk>/match', views.UserMatchView.as_view()),
]
