import json
from hashlib import md5
from django.conf import settings
from decimal import Decimal

from booking.models import Order, Certificate, Flights


def robokassa_get_param_str(total, inv_id):
    mrh_login = settings.ROBOKASSA_SHOP
    if settings.ROBOKASSA_IN_TESTING:
        pass1 = settings.ROBOKASSA_TEST_PASS1
    else:
        pass1 = settings.ROBOKASSA_PASS1

    inv_desc = f'Оплата заказа №{inv_id}'
    crc = md5(f"{mrh_login}:{total}:{inv_id}:{pass1}".encode()).hexdigest()
    payment_params = f"MerchantLogin={mrh_login}&OutSum={total}&InvoiceID={inv_id}" \
                     f"&Description={inv_desc}&SignatureValue={crc}"

    if settings.ROBOKASSA_IN_TESTING:
        payment_params += "&IsTest=1"

    return payment_params


def robokassa_check_crc(request, url_type):
    """
    Проверка ответа Робокассы
    В случае успеха - подтверждение заказа
    """
    if settings.ROBOKASSA_IN_TESTING:
        robokassa_pass2 = settings.ROBOKASSA_TEST_PASS2
    else:
        robokassa_pass2 = settings.ROBOKASSA_PASS2

    out_summ = request.GET['OutSum']
    inv_id = request.GET['InvId']
    crc = request.GET['SignatureValue'].upper()

    my_crc = md5(f"{out_summ}:{inv_id}:{robokassa_pass2}".encode()).hexdigest().upper()
    if crc != my_crc:
        print(f'failure with checking {url_type}: "{my_crc}" vs "{crc}"')
        return

    from .utils import confirm_order
    order = Order.objects.get(pk=inv_id)
    if order.sum != Decimal(out_summ):
        print(f'failure with sum assertion: {url_type}')
        return

    order.payed = True
    order.status = 'payed'
    order.save()

    response = confirm_order(order.order_id, out_summ, order.owner_id, inv_id)
    if response['status'] == 1:
        # TODO перенести вынести функционал создания полетов/сертификатов в другой модуль
        if order.type == 'buy_certificate':
            details = json.loads(response['description'])
            for certificate in details:
                cert_number = certificate['number']
                possible_certs = Certificate.objects.filter(cert_number=cert_number)
                if possible_certs.count():
                    continue

                cer = Certificate.objects.create(owner=order.owner,
                                                 cert_type=certificate['type'],
                                                 cert_number=cert_number,
                                                 flight_time=certificate['time'],
                                                 order=order)

        elif order.type == 'buy_tariff':
            booked_flight = json.loads(response['description'])
            flight_id = booked_flight['flight_id']
            possible_flight = Flights.objects.filter(order=order, remote_record_id=flight_id)
            if not possible_flight.count():
                fl = Flights.objects.create(owner=order.owner,
                                            flight_time=booked_flight['flight_time'],
                                            flight_date=booked_flight['flight_date'],
                                            flight_type=booked_flight['КR'],
                                            remote_record_id=booked_flight['flight_id'],
                                            order=order,
                                            status='payed',
                                            flight_data=json.dumps(booked_flight['details']))

    else:
        print('error with 1c ws')

