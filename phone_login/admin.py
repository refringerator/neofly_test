from django.contrib import admin

from .models import PhoneToken
from django.contrib.auth import get_user_model


class PhoneTokenAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp', 'timestamp', 'attempts', 'used')
    search_fields = ('phone_number', )
    list_filter = ('timestamp', 'attempts', 'used')
    readonly_fields = ('phone_number', 'otp', 'timestamp', 'attempts')


@admin.register(get_user_model())
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number', 'last_name', 'first_name', 'email',
                    'date_joined', 'is_deposit_available')
    list_filter = ('is_deposit_available', 'deposit_minutes', 'date_joined')
    search_fields = (
        'phone_number',
        'last_name',
        'first_name',
        'email',

    )


admin.site.register(PhoneToken, PhoneTokenAdmin)

