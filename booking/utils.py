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
