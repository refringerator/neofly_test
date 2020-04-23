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
    head = []
    rows = []

    for cert_data in certs.availableCertificate:
        rows.append({'cert_type': cert_data.certificateType, 'flight_time': cert_data.flightTime, 'price': cert_data.price})


    return {'head': head, 'rows': rows}


def get_user_id(request):
    return request.user.id or settings.WS_DEFAULT_USER_ID
