from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from django.contrib.auth import get_user_model
from django.core.cache import cache
from booking.models import Certificate, Flights
from .serializers import UserSerializer, FlightSerializer, CertificateSerializer
import datetime


class UserListView(APIView):
    # authentication_classes = (BasicAuthentication, )
    # permission_classes = (IsAuthenticated, )

    def get(self, request):
        user_model = get_user_model()
        items = user_model.objects.all()
        serializer = UserSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):

    def get(self, request, pk=None, phone=None):
        user_model = get_user_model()
        if pk:
            item = get_object_or_404(user_model, pk=pk)
        else:
            item = get_object_or_404(user_model, phone_number=phone)
        serializer = UserSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk=None, phone=None):
        user_model = get_user_model()
        if pk:
            item = get_object_or_404(user_model, pk=pk)
        else:
            item = get_object_or_404(user_model, phone_number=phone)

        serializer = UserSerializer(instance=item, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data)


class CertificateView(APIView):
    # authentication_classes = (BasicAuthentication, )
    # permission_classes = (IsAuthenticated, )

    def get(self, request, cert_number=None):
        item = get_object_or_404(Certificate, cert_number=cert_number)
        serializer = CertificateSerializer(item)
        return Response(serializer.data)

    def put(self, request, cert_number=None):
        item = get_object_or_404(Certificate, cert_number=cert_number)
        serializer = CertificateSerializer(instance=item, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data)


class FlightDetailView(APIView):

    def get(self, request, pk=None, remote_record_id=None):
        if pk:
            item = get_object_or_404(Flights, pk=pk)
        else:
            item = get_object_or_404(Flights, remote_record_id=remote_record_id)
        serializer = FlightSerializer(item)
        return Response(serializer.data)

    # def put(self, request, pk=None, remote_record_id=None):
    #     if pk:
    #         item = get_object_or_404(Flights, pk=pk)
    #     else:
    #         item = get_object_or_404(Flights, remote_record_id=remote_record_id)
    #
    #     serializer = FlightSerializer(instance=item, data=request.data, partial=True)
    #
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #
    #     return Response(serializer.data)

    def post(self, request, remote_record_id):
        is_used = request.data.get('is_used')
        flight_date = request.data.get('flight_date')
        status = request.data.get('status')

        items = Flights.objects.filter(remote_record_id=remote_record_id)
        for item in items:
            item.status = status
            item.flight_date = flight_date
            item.is_used = is_used
            item.save()

        return Response({'done': True})


def clear_cache(request, iso_date_time):
    print("ОЧИТСКА КЕША")
    try:
        date = datetime.datetime.strptime(iso_date_time, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"ошибка {e}")
        return

    redis_month_key = f"booking:month#{date.replace(day=1).date().isoformat()}"
    cache.delete(redis_month_key)
    return Response({'done': True})
