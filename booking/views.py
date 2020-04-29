import calendar

from datetime import datetime

from django.shortcuts import render, redirect
from rest_framework.utils import json

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


def payment_method_selection(request, time=None):
    try:
        date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return redirect('date_selection')

    res = get_available_tariffs(slot_time=date, user_id=get_user_id(request))
    minutes_available = res.minutesAvailable
    tariffs = {}
    for el in res.Items.availableTariff:
        tariffs[el.tariffId] = {
                'count': 0,
                'total': 0,
                'id': el.tariffId,
                'name': el.name,
                'step': el.step,
                'min_time': el.minTime,
                'price': [{'from': it['from'], 'to': it.to, 'pr': it.price} for it in el.tariffDetails.detail]
            }

    context = {
        'tariffs': tariffs,
        'minutes_available': minutes_available,
    }
    return render(request, 'booking/payment_method_selection.html', context)


def buy_certificate(request):
    certs = get_available_certificate_types(user_id=get_user_id(request))
    head, rows = make_cert_table(certs)

    context = {
        'head': head,
        'rows': rows,
    }
    return render(request, 'booking/certificate.html', context=context)


def order_confirmation(request):
    # проверяем, что залогинены

    # потом запрос у 1с на правильность расчета суммы по параметрам

    # потом сохраняем заказ в бд, присваиваем идентификатор
    inv_id = 0

    # если не ок, возвращаем ошибку
    # если ок, отображаем шаблон с кнопкой оплаты

    data = json.loads(request.POST['order'])
    total = 0
    details = []
    is_cert = isinstance(data, list)
    if is_cert:
        values = data
    else:
        values = data.values()

    for tariff_row in values:
        row_total = tariff_row['total']
        if row_total <= 0:
            continue

        item_name = 'Сертификат' if is_cert else 'Тариф'
        description = f"{item_name} {tariff_row['name']} - {tariff_row['count']} мин."
        details.append({'description': description, 'price': row_total})
        total += row_total

    payment_params = robokassa_get_param_str(total, inv_id)

    context = {
        'payment_params': payment_params,
        'total': total,
        'details': details,
    }
    return render(request, 'booking/modal_confirmation.html', context=context)
