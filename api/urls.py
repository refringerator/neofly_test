from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('users/', views.UserListView.as_view()),
    path('users/<int:pk>', views.UserDetailView.as_view()),
    path('users/<str:phone>', views.UserDetailView.as_view()),

    path('flights/', views.FlightListView.as_view()),
    path('flights/<int:pk>', views.FlightDetailView.as_view()),
    path('flights/<str:remote_record_id>', views.FlightDetailView.as_view()),

    path('certificates/<str:cert_number>', views.CertificateView.as_view()),

    path('clear_cache/<str:iso_date_time>', views.clear_cache),
]
