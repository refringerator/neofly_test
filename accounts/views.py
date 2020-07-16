from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views
from django.urls import reverse_lazy
from django.conf import settings

from booking.models import Certificate, Order, Flights
from booking.utils import get_submenu
from .forms import RegisterForm

import requests


@login_required()
def certificates(request):
    certs = Certificate.objects.filter(owner=request.user, is_used=False)
    context = {
        'certificates': certs,
        'submenu': get_submenu('lk'),
    }
    return render(request, 'lk/certificates.html', context)


@login_required()
def flight_records(request):
    flights = Flights.objects.filter(owner=request.user)
    context = {
        'flights': flights,
        'submenu': get_submenu('lk'),
    }
    return render(request, 'lk/flights.html', context)


@login_required()
def orders(request):
    order_list = Order.objects.filter(owner=request.user)
    context = {
        'orders': order_list,
        'submenu': get_submenu('lk'),
    }
    return render(request, 'lk/orders.html', context)


class Logout(views.LogoutView):
    next_page = reverse_lazy('login')


def login_page(request):
    context = {
        'otp_length': settings.PHONE_LOGIN_OTP_LENGTH,
        'submenu': get_submenu('flight'),
    }
    return render(request, 'lk/login.html', context)


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

            # пнуть 1c
            url = settings.SOAP_WSDL.replace('ws/neofly?wsdl', f'hs/neofly/{user.id}/{str(user.phone_number)}/update')

            try:
                requests.post(url=url, json={
                                                'last_name': user.last_name,
                                                'first_name': user.first_name,
                                                'email': user.email,
                                            }
                              , auth=('adm', ''))
            except:
                pass

            return JsonResponse({'status': 'ok'})
        else:
            return HttpResponseBadRequest()

    form.data = {
        'email': request.user.email,
        'surname': request.user.last_name,
        'name': request.user.first_name,
    }

    context = {'form': form}
    return render(request, 'lk/modal_register.html', context)


@login_required()
def lk(request):
    return flight_records(request)


@login_required()
def personal_info(request):
    u = request.user
    dep1 = 'Депозит доступен' if u.is_deposit_available else 'Депозит не доступен'
    dep2 = f'на депозите {u.deposit_minutes} мин.'
    context = {
        'fio': f'{u.first_name} {u.last_name}',
        'email': u.email,
        'phone': f'{u.phone_number}',
        'deposit': f'{dep1}, {dep2}',
        'submenu': get_submenu('lk'),
    }
    return render(request, 'lk/personal_info.html', context)
