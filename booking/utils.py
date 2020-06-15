from collections import defaultdict
from datetime import timedelta

from django.conf import settings
import zeep
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken


def init_soap_client():
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
    fl_time = []

    d = defaultdict(list)
    for cert_data in certs.availableCertificate:
        d[cert_data.certificateType].append({'flight_time': cert_data.flightTime,
                                             'price': cert_data.price,
                                             'disabled': ''
                                             })
        fl_time.append(cert_data.flightTime)

    fl_time.sort()
    head = set(fl_time)

    for key, value in d.items():
        fts = set([v['flight_time'] for v in value])
        for el in head - fts:
            d[key].append({'flight_time': el, 'price': '-', 'disabled': 'disabled'})

        d[key].sort(key=lambda element: element['flight_time'])

    return head, dict(d)


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

    return res.invoiceId


def confirm_order(invoice_id, total, user_id):
    client = init_soap_client()
    res = client.service.confirmOrder(invoiceId=invoice_id, UserId=user_id, total=total)
    return res


def check_certificate(cert_number, user_id):
    client = init_soap_client()
    res = client.service.checkCertificate(certificateNumber=cert_number, UserId=user_id)
    return res

