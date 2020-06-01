import logging
import unicodedata


from django.conf import settings
from . import smsc_api

from sendsms.backends.base import BaseSmsBackend


log = logging.getLogger(__name__)


class SmsBackend(BaseSmsBackend):


    def __init__(self, fail_silently=False, **kwargs):
        super(SmsBackend, self).__init__(fail_silently=fail_silently, **kwargs)
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        """Initializes sms.sluzba.cz API library."""
        self.client = SmsGateApi(getattr(settings, 'SMS_SLUZBA_API_LOGIN', ''),
                                 getattr(settings, 'SMS_SLUZBA_API_PASSWORD', ''),
                                 getattr(settings, 'SMS_SLUZBA_API_TIMEOUT', 2),
                                 getattr(settings, 'SMS_SLUZBA_API_USE_SSL', True))

    def close(self):
        """Cleaning up the reference for sms.sluzba.cz API library."""
        self.client = None

    def send_messages(self, messages):
        """Sending SMS messages via sms.sluzba.cz API.

        Note:
          This method returns number of actually sent sms messages
          not number of SmsMessage instances processed.

        :param messages: list of sms messages
        :type messages: list of sendsms.message.SmsMessage instances
        :returns: number of sent sms messages
        :rtype: int

        """
        count = 0
        for message in messages:
            message_body = unicodedata.normalize('NFKD', unicode(message.body)).encode('ascii', 'ignore')
            for tel_number in message.to:
                try:
                    self.client.send(tel_number, message_body, getattr(settings, 'SMS_SLUZBA_API_USE_POST', True))
                except Exception:
                    if self.fail_silently:
                        log.exception('Error while sending sms via sms.sluzba.cz backend API.')
                    else:
                        raise
                else:
                    count += 1

        return count