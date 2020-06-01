from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.conf import settings

from .models import PhoneToken

User = get_user_model()


class PhoneTokenCreateSerializer(ModelSerializer):
    phone_number = serializers.CharField(validators=PhoneNumberField().validators)

    class Meta:
        model = PhoneToken
        fields = ('pk', 'phone_number') if not settings.PHONE_LOGIN_DEBUG else ('pk', 'phone_number', 'otp')


class PhoneTokenUser(ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class PhoneTokenValidateSerializer(ModelSerializer):
    pk = serializers.IntegerField()
    otp = serializers.CharField(max_length=40)

    class Meta:
        model = PhoneToken
        fields = ('pk', 'otp')
