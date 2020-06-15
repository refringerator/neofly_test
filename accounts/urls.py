from django.urls import path
from . import views


urlpatterns = [
    path('certificates/', views.certificates, name='certificates'),
    path('orders/', views.orders, name='orders'),
    path('flights/', views.flight_records, name='flights'),

    path('login/', views.login_page, name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('register/', views.additional_info_page, name='register'),
]
