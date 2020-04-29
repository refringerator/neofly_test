from hashlib import md5
from django.conf import settings


def robokassa_get_param_str(total, inv_id):
    mrh_login = settings.ROBOKASSA_SHOP
    if settings.ROBOKASSA_IN_TESTING:
        pass1 = settings.ROBOKASSA_TEST_PASS1
        pass2 = settings.ROBOKASSA_TEST_PASS2
    else:
        pass1 = settings.ROBOKASSA_PASS1
        pass2 = settings.ROBOKASSA_PASS2

    inv_desc = f'Оплата заказа №{inv_id}'
    crc = md5(f"{mrh_login}:{total}:{inv_id}:{pass1}".encode()).hexdigest()
    payment_params = f"MerchantLogin={mrh_login}&OutSum={total}&InvoiceID={inv_id}" \
                     f"&Description={inv_desc}&SignatureValue={crc}"

    if settings.ROBOKASSA_IN_TESTING:
        payment_params += "&IsTest=1"

    return payment_params
