from django.urls import path
from . import views

urlpatterns = [

    path('', views.index, name='home'),
    path('time_selection/<int:year>-<int:month>-<int:day>/', views.time_selection, name='time_selection'),
    path('time_selection/', views.time_selection, name='time_selection'),
    path('date_selection/<int:year>-<int:month>/', views.date_selection, name='date_selection'),
    path('date_selection/', views.date_selection, name='date_selection'),
    path('payment_method_selection/<str:time>', views.payment_method_selection, name='payment_method_selection'),
    path('buy_certificate/', views.buy_certificate, name='buy_certificate'),
    path('confirmation/', views.order_confirmation, name='order_confirmation'),
    path('success_payment/<str:url_type>/', views.success_payment, name='success_payment'),




]
