from django.urls import path, include

from api_app import views

app_name = 'api'

urlpatterns = [
    path('clients/create/', views.UserCreateView.as_view()),
    # path('list/', views.UserListView.as_view()),
]
