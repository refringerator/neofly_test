import calendar
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

from rest_framework.utils import json

from .models import *
from .utils import *
from .robokassa import *


def index(request):
    return redirect('date_selection')


def date_selection(request, year=None, month=None):

    if month and year:
        try:
            date_in_month = datetime(year=year, month=month, day=1)
        except ValueError:
            date_in_month = datetime.now()
    else:
        date_in_month = datetime.now()

    items = get_available_dates(date_in_month, user_id=get_user_id(request))
    dates = available_dates_to_dict(items)

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
                         'disabled': 'disabled' if minutes_available <= 0 else '',
                         'style': 'btn-outline-danger' if day.weekday() >= 5 else 'btn-outline-secondary',
                         })

    context = {
        'booking_data': weeks,
        'month_name': date_in_month.strftime('%B'),
        'month': date_in_month.date().isoformat(),
        # 'form': form,
    }
    return render(request, 'booking/date_selection.html', context)


def time_selection(request, year=None, month=None, day=None):
    try:
        date = datetime(year=year, month=month, day=day)
    except ValueError:
        return redirect('date_selection')

    items = get_available_slots(date, user_id=get_user_id(request))

    slots = []
    for slot in items.availableElement:
        slots.append(
            {
                'date': slot.startDate,
                'time': f"{slot.startDate.strftime('%Y-%m-%dT%H:%M:%S')}",
                'minutesAvailable': slot.minutesAvailable,
                'description': slot_name(slot),
                'disabled': 'disabled' if slot.minutesAvailable <= 0 else '',
                'style': 'btn-outline-warning' if 0 < slot.minutesAvailable < 30 else 'btn-outline-secondary',
            }
        )

    context = {
        'slots': slots,
        # 'form': form,
    }
    return render(request, 'booking/time_selection.html', context)


@login_required(login_url='login')
def payment_method_selection(request, time=None):
    try:
        date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return redirect('date_selection')

    res = get_available_tariffs(slot_time=date, user_id=get_user_id(request))
    minutes_available = res.minutesAvailable
    tariffs = {}
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
    }
    return render(request, 'booking/payment_method_selection.html', context)


@login_required(login_url='login')
def buy_certificate(request):
    certs = get_available_certificate_types(user_id=get_user_id(request))
    head, rows = make_cert_table(certs)

    context = {
        'head': head,
        'rows': rows,
    }
    return render(request, 'booking/certificate.html', context=context)


@login_required(login_url='login')
def order_confirmation(request):
    data = json.loads(request.POST['order'])
    total = 0
    details = []
    is_cert = isinstance(data, list)
    if is_cert:
        values = data
        booking_date = None
    else:
        values = data.values()
        booking_date = request.POST['booking_date']

    for tariff_row in values:
        row_total = tariff_row['total']
        if row_total <= 0:
            continue

        item_name = 'Сертификат' if is_cert else 'Тариф'
        description = f"{item_name} {tariff_row['name']} - {tariff_row['count']} мин."
        details.append({'description': description, 'price': row_total})
        total += row_total

    # потом запрос у 1с на правильность расчета суммы по параметрам
    order_id = create_order(user_id=get_user_id(request), is_cert=is_cert, data=data, booking_date=booking_date)

    # потом сохраняем заказ в бд, присваиваем идентификатор
    order = Order.objects.create(sum=total,
                                 order_id=order_id,
                                 order_data=request.POST['order'],
                                 owner=request.user,
                                 status='new',
                                 type='certificate' if is_cert else 'flightTime')

    payment_params = robokassa_get_param_str(total, order.id)

    # мб потом добавить проверку, чтобы заказы не дублировались при закрытии/открытии окошка
    context = {
        'payment_params': payment_params,
        'total': total,
        'details': details,
    }
    return render(request, 'booking/modal_confirmation.html', context=context)


def success_payment(request, url_type):
    print('Payment result: ', url_type)

    # Ошибка оплаты, перенаправляем домой
    if url_type == 'fail':
        context = {
            'title': 'Ошибка при оплате заказа!',
            'message': 'При оплате заказа произошла ошибка',
        }
        return render(request, 'booking/info.html', context=context)

    # Успешная оплата
    robokassa_check_crc(request, url_type)
    if url_type == 'result':  # подтверждение с кассы
        return HttpResponse('OK')

    return redirect('home')  # либо с пользователя

