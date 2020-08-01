from rest_framework import serializers
from django.contrib.auth import get_user_model
from booking.models import Certificate, Flights


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'phone_number',
                  'first_name', 'last_name',
                  'is_deposit_available', 'deposit_minutes']

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.is_deposit_available = validated_data.get('is_deposit_available', instance.is_deposit_available)
        instance.deposit_minutes = validated_data.get('deposit_minutes', instance.deposit_minutes)

        instance.save()
        return instance


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'cert_number', 'cert_type', 'is_used']

    def update(self, instance, validated_data):
        instance.is_used = validated_data.get('is_used', instance.is_used)

        instance.save()
        return instance


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flights
        fields = ['is_used', 'flight_date', 'status', 'flight_time',
                  'flight_data', 'owner', 'status', 'remote_record_id']

    # def create(self, instance, validated_data):
    #     return Flights.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.is_used = validated_data.get('is_used', instance.is_used)
        instance.flight_date = validated_data.get('flight_date', instance.flight_date)
        instance.status = validated_data.get('status', instance.status)
        instance.flight_time = validated_data.get('flight_time', instance.flight_time)
        instance.flight_data = validated_data.get('flight_data', instance.flight_data)
        instance.remote_record_id = validated_data.get('remote_record_id', instance.remote_record_id)

        instance.save()
        return instance
