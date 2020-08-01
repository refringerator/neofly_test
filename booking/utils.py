# TODO Вынести работу с сервисом 1с в отдельный модуль

from collections import defaultdict
from datetime import timedelta
import json

from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse

from requests import Session
from requests.auth import HTTPBasicAuth
import zeep
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken

from booking.models import Flights


def init_soap_client():
    """
    Инициализация SOAP клиента
    Вроде как, установка соединения и получение WSDL-схемы
    """
    session = Session()
    session.auth = HTTPBasicAuth(settings.WS_PROXY_LOGIN, settings.WS_PROXY_PASS)
    session.verify = not settings.WS_IGNORE_SSL

    client = zeep.Client(wsdl=settings.SOAP_WSDL,
                         wsse=UsernameToken(settings.WS_LOGIN, settings.WS_PASS),
                         transport=Transport(session=session))
    return client


def available_dates_to_dict(dates):
    if dates is None:
        return {}

    return {item.startDate: item.minutesAvailable for item in dates.availableElement}


def slot_name(slot):
    return f"{slot.startDate.strftime('%H:%M')}" \
           f" - " \
           f"{(slot.startDate + timedelta(minutes=30)).strftime('%H:%M')}" \
           f" ({slot.minutesAvailable} мин.) "


def get_available_dates(date_in_month, user_id):
    client = init_soap_client()
    res = client.service.getAvailableDates(Month=date_in_month, UserId=user_id)
    return res.Items


def get_available_slots(slot_date, user_id):
    client = init_soap_client()
    res = client.service.getAvailableSlots(Date=slot_date, UserId=user_id)
    return res.Items


def get_available_certificate_types(user_id):
    client = init_soap_client()
    res = client.service.getAvailableCertificateTypes(UserId=user_id)
    return res.certificates


def get_available_tariffs(slot_time, user_id):
    client = init_soap_client()
    res = client.service.getAvailableTariffs(SlotTime=slot_time, UserId=user_id)
    return res


def make_cert_table(certs):
    flight_time = []

    certificates = defaultdict(list)
    for cert_data in certs.availableCertificate:
        certificates[cert_data.certificateType].append({'flight_time': cert_data.flightTime,
                                                        'price': cert_data.price,
                                                        'disabled': ''
                                                        })
        flight_time.append(cert_data.flightTime)

    head = set(flight_time)

    for key, value in certificates.items():
        fts = set([v['flight_time'] for v in value])
        for el in head - fts:
            certificates[key].append({'flight_time': el, 'price': '-', 'disabled': 'disabled'})

        certificates[key].sort(key=lambda element: element['flight_time'])

    return sorted(head), dict(certificates)


def get_user_id(request):
    return request.user.id or settings.WS_DEFAULT_USER_ID


def create_order(user_id, order_type, data, booking_date):
    client = init_soap_client()

    if order_type == 'buy_certificate':
        order_data = {
            'newCertificates':
                {
                    'newCertificate': [
                        {
                            'certificateType': x['name'],
                            'flightTime': x['count'],
                            'price': x['total']
                        }
                        for x in data]}

        }

        total = sum(item['price'] for item in order_data['newCertificates']['newCertificate'])

    elif order_type == 'flight_certificate':
        order_data = {
            'flightTime':
                {'bookingDate': str(booking_date).replace('"', ''),
                 'certificates':
                     {'certificate': [
                         {'number': x['number'],
                          'certificateType': x['certificateType'],
                          'flightTime': x['flightTime']
                          }
                         for x in data
                     ]}
                 }
        }
        total = 0

    elif order_type == 'flight_deposit':
        order_data = {
            'flightTime':
                {'bookingDate': str(booking_date).replace('"', ''),
                 'depositMinutes': data['deposit_selected']
                 }
            }
        total = 0

    elif order_type == 'buy_deposit':
        order_data = {
            'depositMinutes': data['depositMinutes']
        }
        total = data['total']

    elif order_type == 'buy_tariff':
        values = data.values()
        order_data = {
            'flightTime':
                {'bookingDate': str(booking_date).replace('"', ''),
                 'tariffRecords':
                    {'record': [
                        {'tariffId': x['id'],
                         'minutes': x['count'],
                         'sum': x['total']
                         }
                        for x in values if x['count']
                        ]}
                    }
            }

        total = sum(item['sum'] for item in order_data['flightTime']['tariffRecords']['record'])

    order_data['total'] = total
    order_data['UserId'] = user_id

    res = client.service.createOrder(Data=order_data)

    # здесь проверка статуса
    # если не 1, тогда дернуть сентри с ошибкой
    # и как-то обработать дальнейшие действия

    return res.invoiceId


def update_user_info(phone_number, user_id):
    """Обновление данных пользователя по данным 1с"""
    client = init_soap_client()
    res = client.service.getUserInfo(PhoneNumber=phone_number, UserId=user_id)
    if res.status == 1:
        user_model = get_user_model()
        user = user_model.objects.filter(id=user_id)[0]
        if user:
            user.last_name = res.lastName
            user.first_name = res.firstName
            user.deposit_minutes = res.isDepositAvailable
            user.is_deposit_available = res.isDepositAvailable
            if res.email:
                user.email = res.email
            user.save()


def confirm_order(invoice_id, total, user_id, order_id):
    """Подтверждение заказа"""
    client = init_soap_client()
    res = client.service.confirmOrder(invoiceId=invoice_id,
                                      UserId=user_id,
                                      total=total,
                                      orderId=order_id)
    return res


def check_certificate(cert_number, user_id):
    client = init_soap_client()
    res = client.service.checkCertificate(certificateNumber=cert_number, UserId=user_id)
    return res


def get_submenu(kind):
    """
    Получение списка элементов подменюшки
    Состав зависит от текущего положения: личный кабинет или бронирование полета
    """
    submenu = []
    if kind == 'flight':
        submenu.append({'name': 'Запись на полет', 'url': reverse('date_selection')})
        submenu.append({'name': 'Купить сертификат', 'url': reverse('buy_certificate')})

    elif kind == 'lk':
        submenu.append({'name': 'Мой кабинет', 'url': reverse('lk')})
        submenu.append({'name': 'Заказы', 'url': reverse('orders')})
        submenu.append({'name': 'Сертификаты', 'url': reverse('certificates')})
        submenu.append({'name': 'Полеты', 'url': reverse('flights')})

    return submenu


def get_month_name(month_name):
    """Получение названия месяца на русском языке"""
    d = {'January': 'Январь',
         'February': 'Февраль',
         'March': 'Март',
         'April': 'Апрель',
         'May': 'Май',
         'June': 'Июнь',
         'July': 'Июль',
         'August': 'Август',
         'September': 'Сентябрь',
         'October': 'Октябрь',
         'November': 'Ноябрь',
         'December': 'Декабрь'
         }

    return d.get(month_name, month_name)


def create_flight_by_response(response, order):
    booked_flight = json.loads(response['description'])[0]  # бред в 1с
    flight_id = booked_flight['flight_id']
    possible_flight = Flights.objects.filter(order=order, remote_record_id=flight_id)
    if not possible_flight.count():
        fl = Flights.objects.create(owner=order.owner,
                                    flight_time=booked_flight['flight_time'],
                                    flight_date=booked_flight['flight_date'],
                                    flight_type=booked_flight['flight_type'],
                                    remote_record_id=booked_flight['flight_id'],
                                    order=order,
                                    status='payed',
                                    flight_data=json.dumps(booked_flight['details']))
