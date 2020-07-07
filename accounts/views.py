from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, views
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.conf import settings

from booking.models import Certificate, Order, Flights
from booking.utils import get_submenu
from .forms import RegisterForm



@login_required()
def certificates(request):
    certs = Certificate.objects.filter(owner=request.user, is_used=False)
    context = {
        'certificates': certs,
        'submenu': get_submenu('lk'),
    }
    return render(request, 'booking/certificates.html', context)


@login_required()
def flight_records(request):
    flights = Flights.objects.filter(owner=request.user)
    context = {
        'flights': flights,
        'submenu': get_submenu('lk'),
    }
    return render(request, 'booking/flights.html', context)


@login_required()
def orders(request):
    order_list = Order.objects.filter(owner=request.user)
    context = {
        'orders': order_list,
        'submenu': get_submenu('lk'),
    }
    return render(request, 'booking/orders.html', context)


class Logout(views.LogoutView):
    next_page = reverse_lazy('login')


def login_page(request):
    context = {'otp_length': settings.PHONE_LOGIN_OTP_LENGTH}
    return render(request, 'booking/login.html', context)


@login_required()
def additional_info_page(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = request.user
            user.last_name = cd['surname']
            user.first_name = cd['name']
            user.email = cd['email']
            user.save()

            return JsonResponse({'status': 'ok'})

    form.data = {
        'email': request.user.email,
        'surname': request.user.last_name,
        'name': request.user.first_name,
    }

    context = {'form': form}
    return render(request, 'booking/modal_register.html', context)


@login_required()
def user_logout(request):  # удалить
    logout(request)
    return redirect('home')


@login_required()
def lk(request):
    return flight_records(request)