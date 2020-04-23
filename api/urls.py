

from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('users/', views.UserListView.as_view()),
    path('users/<int:pk>', views.UserDetailView.as_view()),
    path('users/<str:phone>', views.UserDetailView.as_view()),
]
