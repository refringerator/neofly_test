from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import PhoneToken
from .serializers import (
    PhoneTokenCreateSerializer, PhoneTokenValidateSerializer
)
from .utils import user_detail


class GenerateOTP(CreateAPIView):
    queryset = PhoneToken.objects.all()
    serializer_class = PhoneTokenCreateSerializer

    def post(self, request, format=None):
        # Get the patient if present or result None.
        ser = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        if ser.is_valid():
            token = PhoneToken.create_otp_for_number(
                request.data.get('phone_number')
            )
            if token:
                phone_token = self.serializer_class(
                    token, context={'request': request}
                )
                return Response(phone_token.data)
            return Response({
                'reason': "Вы не можете получать более {n} кодов в день, пожалуйста, попробуйте завтра".format(
                    n=getattr(settings, 'PHONE_LOGIN_ATTEMPTS', 10))}, status=status.HTTP_403_FORBIDDEN)
        return Response(
            {'reason': ser.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)


class ValidateOTP(CreateAPIView):
    queryset = PhoneToken.objects.all()
    serializer_class = PhoneTokenValidateSerializer

    def post(self, request, format=None):
        # Get the patient if present or result None.
        ser = self.serializer_class(
            data=request.data, context={'request': request}
        )
        if ser.is_valid():
            pk = request.data.get("pk")
            otp = request.data.get("otp")
            try:
                user = authenticate(request, pk=pk, otp=otp)
                if user:
                    last_login = user.last_login
                login(request, user)
                response = user_detail(user, last_login)

                # TODO перенести в норм место
                model_user = get_user_model()
                u = model_user.objects.get(pk=request.user.id)
                if not u.last_name or not u.first_name:
                    response['need_registration'] = True

                if order_type := request.session.get('order_type'):
                    date_time = str(request.session.get('booking_date')).replace('"', '')  # TODO Убрать кавычки сразу при закладке параметра
                    response['next'] = reverse('buy_certificate') if order_type == 'buy_certificate' else reverse('payment_method_selection', kwargs={'time': date_time})
                return Response(response, status=status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response(
                    {'reason': "Одноразовый пароль не существует"},  # OTP doesn't exist
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
        return Response(
            {'reason': ser.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
