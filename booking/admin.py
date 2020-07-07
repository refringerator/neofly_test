from django.contrib import admin

from .models import Certificate, Flights, Order


@admin.register(Flights)
class FlightsAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'date_created', 'flight_date',
                    'is_used', 'remote_record_id', 'flight_time', 'flight_type', 'status')
    list_filter = ('status', 'date_created', 'flight_date')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'cert_number', 'owner', 'order', 'date_created',
                    'is_used', 'flight_time', 'cert_type')
    list_filter = ('cert_type', 'date_created')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'type', 'date_created', 'order_id', 'sum', 'payed', 'status')
    list_filter = ('status', 'date_created')

