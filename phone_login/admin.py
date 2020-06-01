from django.contrib import admin

from .models import PhoneToken
from django.contrib.auth import get_user_model


class PhoneTokenAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp', 'timestamp', 'attempts', 'used')
    search_fields = ('phone_number', )
    list_filter = ('timestamp', 'attempts', 'used')
    readonly_fields = ('phone_number', 'otp', 'timestamp', 'attempts')


admin.site.register(PhoneToken, PhoneTokenAdmin)
admin.site.register(get_user_model())
