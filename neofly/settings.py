import os
import environ

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOST=(str, '*')
)

# reading .env file
environ.Env.read_env()

# False if not in os.environ
DEBUG = env('DEBUG')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = [env('ALLOWED_HOST')]
INTERNAL_IPS = [
    '127.0.0.1',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'debug_toolbar',
    'rest_framework',
    'rest_framework.authtoken',

    'phone_login',
    'booking',
    'accounts',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'neofly.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'neofly.wsgi.application'

DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    'default': env.db(),
    'extra': env.db('SQLITE_URL', default='sqlite:////db.sqlite3')
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

STATIC_ROOT = env('STATIC_ROOT')
STATIC_URL = '/static/'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    # ]
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'phone_login.backends.phone_backend.PhoneBackend',

]

LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

# SOAP WS
SOAP_WSDL = env('SOAP_WSDL')
WS_LOGIN = env('WS_LOGIN')
WS_PASS = env('WS_PASS')
WS_PROXY_LOGIN = env('WS_PROXY_LOGIN')
WS_PROXY_PASS = env('WS_PROXY_PASS')
WS_IGNORE_SSL = env('WS_IGNORE_SSL')
WS_DEFAULT_USER_ID = env.int('WS_DEFAULT_USER_ID')

# SENDSMS
SENDSMS_BACKEND = env('SENDSMS_BACKEND')
SENDSMS_FROM_NUMBER = env('SENDSMS_FROM_NUMBER')
SENDSMS_ACCOUNT_SID = env('SENDSMS_ACCOUNT_SID')
SENDSMS_AUTH_TOKEN = env('SENDSMS_AUTH_TOKEN')

# PHONE_LOGIN
PHONE_LOGIN_ATTEMPTS = env.int('PHONE_LOGIN_ATTEMPTS')
PHONE_LOGIN_OTP_LENGTH = env.int('PHONE_LOGIN_OTP_LENGTH')
PHONE_LOGIN_OTP_HASH_ALGORITHM = env('PHONE_LOGIN_OTP_HASH_ALGORITHM')
PHONE_LOGIN_DEBUG = env.bool('PHONE_LOGIN_DEBUG')

# ROBOKASSA
ROBOKASSA_SHOP = env('ROBOKASSA_SHOP')
ROBOKASSA_PASS1 = env('ROBOKASSA_PASS1')
ROBOKASSA_PASS2 = env('ROBOKASSA_PASS2')

ROBOKASSA_IN_TESTING = env.bool('ROBOKASSA_IN_TESTING')
ROBOKASSA_TEST_PASS1 = env('ROBOKASSA_TEST_PASS1')
ROBOKASSA_TEST_PASS2 = env('ROBOKASSA_TEST_PASS2')

AUTH_USER_MODEL = 'phone_login.CustomUser'


# CELERY STUFF
BROKER_URL = 'redis://localhost:6379'
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# SENTRY
if env.bool('USE_SENTRY'):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=env('SENTRY_DNS'),
        integrations=[DjangoIntegration()],

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )

