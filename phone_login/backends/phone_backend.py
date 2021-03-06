import datetime
import json
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from ..models import PhoneToken
from ..utils import model_field_attr

import requests

from accounts.tasks import update_users_info


class PhoneBackend(ModelBackend):
    def __init__(self, *args, **kwargs):
        self.user_model = get_user_model()

    def get_username(self):
        """
        Returns a UUID-based 'random' and unique username.

        This is required data for user models with a username field.
        """
        return str(uuid.uuid4())[:model_field_attr(
            self.user_model, 'username', 'max_length')
               ]

    def create_user(self, phone_token, **extra_fields):
        """
        Create and returns the user based on the phone_token.
        """
        password = self.user_model.objects.make_random_password()
        if extra_fields.get('username'):
            username = extra_fields.get('username')
        else:
            username = self.get_username()
        if extra_fields.get('password'):
            password = extra_fields.get('password')
        else:
            password = password

        phone_number = phone_token.phone_number
        user = self.user_model.objects.create_user(
            username=username,
            password=password,
            phone_number=phone_number,
            **extra_fields
        )
        return user

    def authenticate(self, request, pk=None, otp=None, **extra_fields):
        if pk:
            # 1. Validating the PhoneToken with PK and OTP.
            # 2. Check if phone_token and otp are same, within the given time range
            timestamp_difference = datetime.datetime.now() - datetime.timedelta(
                minutes=getattr(settings, 'PHONE_LOGIN_MINUTES', 10)
            )
            try:

                phone_token = PhoneToken.objects.get(
                    pk=pk,
                    otp=otp,
                    used=False,
                    timestamp__gte=timestamp_difference
                )
            except PhoneToken.DoesNotExist:
                phone_token = PhoneToken.objects.get(pk=pk)
                phone_token.attempts = phone_token.attempts + 1
                phone_token.save()
                raise PhoneToken.DoesNotExist

            # 3. Create new user if he doesn't exist. But, if he exists login.
            user = self.user_model.objects.filter(
                phone_number=phone_token.phone_number
            ).first()
            if not user:
                user = self.create_user(
                    phone_token=phone_token,
                    **extra_fields
                )
                # задача подтянуть данные из 1с
                # credentials = pika.PlainCredentials(settings.RABBIT_USER, settings.RABBIT_PASS)
                # parameters = pika.ConnectionParameters(settings.RABBIT_SERVER, credentials=credentials,
                #                                        virtual_host=settings.RABBIT_VHOST)
                # connection = pika.BlockingConnection(parameters)
                # channel = connection.channel()
                # channel.queue_declare(queue="new_user", durable=True)
                # message = {'user_id': user.id, 'phone_number': str(phone_token.phone_number)}
                # channel.basic_publish(exchange='', routing_key="new_user", body=json.dumps(message))

                # пнуть 1c
                # url = settings.SOAP_WSDL.replace('ws/neofly?wsdl',
                #                                  f'hs/neofly/{user.id}/{str(user.phone_number)}/update')
                #
                # try:
                #     requests.post(url=url, json={
                #         'last_name': user.last_name,
                #         'first_name': user.first_name,
                #         'email': user.email,
                #     }
                #                   , auth=('adm', ''))
                # except:
                #     pass

                from booking.utils import update_user_info
                # update_users_info.delay(user_id=user.id)
                try:
                    update_user_info(phone_number=str(phone_token.phone_number), user_id=user.id)
                except:
                    print("Что-то пошло не так при создании пользователя")

            phone_token.used = True
            phone_token.attempts = phone_token.attempts + 1
            phone_token.save()
            return user
        return None
