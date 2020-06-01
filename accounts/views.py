from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, views
from django.urls import reverse_lazy
from booking.models import Certificate, Order, Flights
from .forms import RegisterForm
from phone_login.backends.phone_backend import PhoneBackend
from phone_login.models import PhoneToken


@login_required(login_url='login')
def certificates(request):
    certs = Certificate.objects.filter(owner=request.user)
    context = {'certificates': certs}
    return render(request, 'booking/certificates.html', context)


@login_required(login_url='login')
def flight_records(request):
    flights = Flights.objects.filter(owner=request.user)
    context = {'flights': flights}
    return render(request, 'booking/flights.html', context)


@login_required(login_url='login')
def orders(request):
    order_list = Order.objects.filter(owner=request.user)
    context = {'orders': order_list}
    return render(request, 'booking/orders.html', context)


class Logout(views.LogoutView):
    next_page = reverse_lazy('login')


def login_page(request):
    # На форме кнопка с отправкой генерированного пина

    # АПИ в фон_логин вьюшках
    # По нажатию через ажакс пост запрос - из ответа сохраняем ПК, тестируем с ответом
    # По Логину - проверка ПК без этой всей байды внизу, эту вьюху вообще удалить

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        otp = request.POST.get('otp')

        token = PhoneToken.create_otp_for_number(phone_number)

        phone_backend = PhoneBackend()
        user = phone_backend.authenticate(request=request, pk=token.id, otp=token.otp)
        login(request, user, backend='phone_login.backends.phone_backend.PhoneBackend')
        return redirect('date_selection')

    context = {}
    return render(request, 'booking/login.html', context)


def register_page(request):  # TODO убрать вообще регистрацию
    if request.user.is_authenticated:  # TODO заменить на декоратор как в уроке
        return redirect('home')

    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            phone_backend = PhoneBackend()
            cd = form.cleaned_data

            phone_number = cd['phone_number']
            token = PhoneToken.create_otp_for_number(phone_number.raw_input)
            del cd['phone_number']
            user = phone_backend.authenticate(request=request, pk=token.id, otp=token.otp, **cd)
            login(request, user, backend='phone_login.backends.phone_backend.PhoneBackend')
            return redirect('date_selection')

    context = {'form': form}
    return render(request, 'booking/register.html', context)


@login_required(login_url='login')
def user_logout(request):  # удалить
    logout(request)
    return redirect('home')

