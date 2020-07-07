import phone_login
from django.conf import settings
from django.contrib import admin
from django.urls import path, include


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('booking.urls')),
    path('phone_login/', include('phone_login.urls')),
    path('api/', include('api.urls')),
    path('accounts/', include('accounts.urls')),

    path('sentry-debug/', trigger_error),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
