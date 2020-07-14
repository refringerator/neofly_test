import calendar
from datetime import datetime
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from rest_framework.utils import json

from accounts.views import additional_info_page
from .booking_service import get_available_date, available_dates_in_month
from .models import Order, Flights
from .robokassa import robokassa_get_param_str, robokassa_check_crc
from .utils import get_user_id, get_month_name, get_submenu, \
    get_available_slots, slot_name, get_available_tariffs, get_available_certificate_types, make_cert_table, \
    create_order, confirm_order, check_certificate


logger = logging.getLogger('django.server')


def index(request):
    return redirect('date_selection')


def date_selection(request, year=None, month=None):

    date_in_month, prev_month_unavailable, next_month_unavailable = get_available_date(year, month)
    dates = available_dates_in_month(date_in_month, get_user_id(request))

    cal = calendar.Calendar()
    weeks = cal.monthdatescalendar(date_in_month.year, date_in_month.month)
    for week in weeks:
        for i in range(7):
            day = week.pop(i)
            cd = datetime.combine(day, datetime.min.time())
            minutes_available = dates.get(cd, 0)
            week.insert(i,
                        {'day': day.strftime("%d"),
                         'value': cd.date().isoformat(),
                         'name': day.strftime("%d %b %Y"),
                         'disabled': 'disabled' if minutes_available < 2 else '',
                         'style': 'btn-outline-danger' if day.weekday() >= 5 else 'btn-outline-secondary',
                         })

    context = {
        'booking_data': weeks,
        'month_name': get_month_name(date_in_month.strftime('%B')),
        'month': date_in_month.date().isoformat(),
        'prev_month_unavailable': prev_month_unavailable,
        'next_month_unavailable': next_month_unavailable,
        'submenu': get_submenu('flight'),
    }

    return render(request, 'booking/date_selection.html', context)


def time_selection(request, year=None, month=None, day=None):
    try:
        date = datetime(year=year, month=month, day=day)
    except ValueError:
        return redirect('date_selection')

    items = get_available_slots(date, user_id=get_user_id(request))

    slots = []
    if items:
        for slot in items.availableElement:
            slots.append(
                {
                    'date': slot.startDate,
                    'time': f"{slot.startDate.strftime('%Y-%m-%dT%H:%M:%S')}",
                    'minutesAvailable': slot.minutesAvailable,
                    'description': slot_name(slot),
                    'disabled': 'disabled' if slot.minutesAvailable < 2 else '',
                    'style': 'btn-outline-warning' if 0 < slot.minutesAvailable < 30 else 'btn-outline-secondary',
                }
            )

    context = {
        'slots': slots,
        'submenu': get_submenu('flight'),
    }
    return render(request, 'booking/time_selection.html', context)


def payment_method_selection(request, time=None):
    try:
        date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return redirect('date_selection')

    res = get_available_tariffs(slot_time=date, user_id=get_user_id(request))
    minutes_available = res.minutesAvailable
    tariffs = {}
    if res.Items:
        for element in res.Items.availableTariff:
            tariffs[element.tariffId] = {
                'count': 0,
                'total': 0,
                'id': element.tariffId,
                'name': element.name,
                'step': element.step,
                'min_time': element.minTime,
                'price': [{'from': it['from'],
                           'to': it.to,
                           'pr': it.price
                           }
                          for it in element.tariffDetails.detail]
            }

    context = {
        'tariffs': tariffs,
        'minutes_available': minutes_available,
        'booking_date': time,
        'booking_date_as_dt': date,
        'deposit_minutes': request.user.deposit_minutes if request.user.is_authenticated else False,
        'submenu': get_submenu('flight'),
    }
    return render(request, 'booking/payment_method_selection.html', context)


def buy_certificate(request):
    certs = get_available_certificate_types(user_id=get_user_id(request))
    head, rows = make_cert_table(certs)

    context = {
        'head': head,
        'rows': rows,
        'submenu': get_submenu('flight'),
    }
    return render(request, 'booking/buy_certificate.html', context=context)


def order_confirmation(request):
    if not request.user.is_authenticated:
        request.session['order'] = request.POST['order']
        request.session['order_type'] = request.POST.get('order_type')
        request.session['booking_date'] = request.POST.get('booking_date', None)
        return render(request, 'lk/modal_login_required.html', context={})

    # Проверка юзера на заполненность
    if not request.user.last_name or not request.user.first_name:
        return additional_info_page(request)

    data = json.loads(request.POST['order'])
    order_type = request.POST.get('order_type')
    booking_date = request.POST.get('booking_date', None)

    total = 0
    flight_time = 0
    details = []

    if order_type == 'buy_certificate':
        values = data

    elif order_type == 'buy_tariff':
        values = data.values()

    elif order_type == 'buy_deposit':
        pass
        # Пока не покупаем на сайте депозит

    elif order_type == 'flight_certificate':
        for cert in data:
            flight_time += cert['flightTime']
            description = f"Полет по сертификату {cert['number']} - {cert['certificateType']}"
            details.append({'description': description, 'flightTime': cert['flightTime']})

    elif order_type == 'flight_deposit':
        flight_time = data['deposit_selected']
        description = f"Полет по депозиту"
        details.append({'description': description, 'flightTime': flight_time})

    if order_type in ['buy_tariff', 'buy_certificate']:
        for tariff_row in values:
            row_total = tariff_row['total']
            if row_total <= 0:
                continue

            item_name = 'Сертификат' if order_type == 'buy_certificate' else 'Тариф'
            description = f"{item_name} {tariff_row['name']} - {tariff_row['count']} мин."
            details.append({'description': description, 'price': row_total})
            total += row_total

    # запрос у 1с на правильность расчета суммы по параметрам
    order_id = create_order(user_id=get_user_id(request),
                            order_type=order_type,
                            data=data,
                            booking_date=booking_date)

    # сохраняем заказ в бд, присваиваем идентификатор
    order = Order.objects.create(sum=total,
                                 order_id=order_id,
                                 order_data=request.POST['order'],
                                 owner=request.user,
                                 status='new',
                                 type=order_type)

    # мб потом добавить проверку, чтобы заказы не дублировались при закрытии/открытии окошка
    context = {
        'total': total,
        'details': details,
    }

    if order_type in ['buy_tariff', 'buy_certificate', 'buy_deposit']:
        template_name = 'booking/modal_confirmation.html'
        context['payment_params'] = robokassa_get_param_str(total, order.id)
        context['total'] = total
    else:
        template_name = 'booking/modal_confirmation_without_payment.html'
        context['order_id'] = order_id
        context['total'] = flight_time

    return render(request, template_name, context=context)


def order_confirmation_without_payment(request, order_id):
    if not request.user.is_authenticated:
        return render(request, 'lk/modal_login_required.html', context={})

    # Проверка юзера на заполненность
    if not request.user.last_name or not request.user.first_name:
        return additional_info_page(request)

    # проверки, что заказ то, что надо, и юзер тот
    order = Order.objects.get(order_id=order_id)
    if order.owner != request.user:
        return HttpResponse('error')

    if order.type not in ['flight_certificate', 'flight_deposit']:
        return HttpResponse('error')

    order.status = 'confirmed'
    order.save()

    # находим заказ и подтверждаем в 1с TODO переделать с invoice и order_id
    response = confirm_order(order_id, total=0, user_id=get_user_id(request), order_id=order_id)

    if response['status'] == 1:
        order = Order.objects.get(order_id=order_id)
        details = json.loads(response['description'])

        if order.type in ['flight_certificate', 'flight_deposit']:
            for flight in details:
                possible_fl = Flights.objects.filter(order=order,
                                                     flight_date=flight['flight_date'],
                                                     flight_type=flight['flight_type']
                                                     )
                if possible_fl.count():
                    continue

                new_fl = Flights.objects.create(owner=order.owner,
                                                flight_time=flight['flight_time'],
                                                flight_date=flight['flight_date'],
                                                flight_type=flight['flight_type'],
                                                remote_record_id=flight['flight_id'],
                                                order=order,
                                                status='payed')

    else:
        logger.error(f'Ошибка вызова сервиса 1с при подтверждении заказа {order_id=} {order.id=}')

    return redirect('flights')


def success_payment(request, url_type):
    logger.info(f'Результат подтверждения оплаты: {url_type=} {request.user=}')

    # Ошибка оплаты, перенаправляем домой
    if url_type == 'fail':
        context = {
            'title': 'Ошибка при оплате заказа!',
            'message': 'При оплате заказа произошла ошибка',
            'submenu': get_submenu('flight'),
        }
        return render(request, 'base/info.html', context=context)

    if request.user.is_authenticated and url_type == 'success':
        context = {
            'title': 'Благодарим за покупку!',
            'message_html': 'Номер приобретенного сертификата можно узнать на странице '
                            '<a href="' + reverse('certificates') + '">мои сертификаты</a>'
                            ', <br>ознакомится с предстоящими полетами на странице '
                            '<a href="' + reverse('flights') + '">полеты</a>.',
            'message': '',
            'submenu': get_submenu('lk'),
        }
        return render(request, 'base/info.html', context=context)

    # Успешная оплата
    robokassa_check_crc(request, url_type)
    if url_type == 'result':  # подтверждение с кассы
        return HttpResponse('OK')

    return redirect('home')  # либо с пользователя


@require_POST
def check_cert(request):
    one_bad_reason = 'Данный сертификат не действвителен.<br>' \
                     'Пожалуйста, введите другой номер сертификата или обратитесь в службу поддержки.'

    cert_number = request.POST.get('cert_number')
    if cert_number:
        cert_number = cert_number.strip()
        try:
            # дергаем данные из 1с
            cert_data = check_certificate(cert_number, get_user_id(request))

            if cert_data.status == 2:
                return JsonResponse({
                    'status': 'error',
                    'description': one_bad_reason if one_bad_reason else cert_data['description']
                })

            cert = cert_data['certificate']
            return JsonResponse({
                'status': 'ok',
                'number': cert['number'],
                'flightTime': cert['flightTime'],
                'certificateType': cert['certificateType']
            })

        except:
            pass
    return JsonResponse({'status': 'error', 'description': one_bad_reason if one_bad_reason else 'Ошибка проверки сертификата'})
