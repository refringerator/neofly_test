from django.contrib import admin

from .models import Certificate, Flights, Order

admin.site.register([Certificate, Flights, Order])
