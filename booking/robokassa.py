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

    response = confirm_order(order.order_id, out_summ, order.owner_id)
    if response['status'] == 1:
        details = json.loads(response['description'])

        if order.type == 'buy_certificate':
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
            for flight in details:
                possible_certs = Flights.objects.filter(order=order,
                                                        flight_date=flight['flight_date'],
                                                        flight_type=flight['flight_type']
                                                        )
                if possible_certs.count():
                    continue

                cer = Flights.objects.create(owner=order.owner,
                                             flight_time=flight['flight_time'],
                                             flight_date=flight['flight_date'],
                                             flight_type=flight['flight_type'],
                                             remote_record_id=flight['flight_id'],
                                             order=order,
                                             status='payed')

    else:
        print('error with 1c ws')

