from django.conf import settings

import requests
import logging

from sendsms.backends.base import BaseSmsBackend


logger = logging.getLogger(__name__)

SMSC_API_URL = "https://smsc.ru/sys/send.php"
SMSC_USERNAME = getattr(settings, "SMSC_LOGIN", "")
SMSC_PASSWORD = getattr(settings, "SMSC_PASSWORD", "")
SMSC_ONLY_BALANCE = getattr(settings, "SMSC_ONLY_BALANCE", True)


class SmsBackend(BaseSmsBackend):
    def get_username(self):
        return SMSC_USERNAME

    def get_password(self):
        return SMSC_PASSWORD

    def get_cost(self):
        return "1" if SMSC_ONLY_BALANCE else "3"

    def _send(self, message):
        """
        Private method to send one message.

        :param SmsMessage message: SmsMessage class instance.
        :returns: True if message is sent else False
        :rtype: bool
        """

        params = {
            "login": self.get_username(),
            "psw": self.get_password(),
            "phones": ",".join(message.to),
            "mes": message.body,
            "charset": "utf-8",
            "fmt": "3",
            "cost": self.get_cost(),
        }

        response = requests.get(SMSC_API_URL, params=params)
        if response.status_code != 200:
            if not self.fail_silently:
                raise Exception("Bad status code")
            else:
                return False

        resp_json = response.json()

        if 'error' in resp_json:  # Получили ошибку
            logger.error(f"Ошибка отправки сообщения {resp_json}")
            if not self.fail_silently:
                raise Exception("Bad result")
            else:
                return False

        if 'cnt' in resp_json:
            return True

        return False

    def send_messages(self, messages):
        """
        Send messages.

        :param list messages: List of SmsMessage instances.
        :returns: number of messages sended successful.
        :rtype: int
        """
        counter = 0
        for message in messages:
            res = self._send(message)
            if res:
                counter += 1

        return counter
