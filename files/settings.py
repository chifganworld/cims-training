from __future__ import absolute_import, unicode_literals

from .settings_common import *  # noqa

HOSTNAME = '192.168.60.2'
TEMBA_HOST = '192.168.60.2'

TESTING = True
DEBUG = TESTING
TEMPLATE_DEBUG = DEBUG
IS_PROD = not TESTING

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.60.2', 'rapidpro']

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 10 if TESTING else 15

BROKER_URL = 'redis://%s:%d/%d' % (REDIS_HOST, REDIS_PORT, REDIS_DB)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://%s:%s/%s" % (REDIS_HOST, REDIS_PORT, REDIS_DB),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'rapidpro',
        'USER': 'rapidpro',
        'PASSWORD': 'rapidpro',
        'HOST': 'localhost',
        'PORT': '',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
        }
    }
}
DATABASES['default']['CONN_MAX_AGE'] = 60
DATABASES['default']['ATOMIC_REQUESTS'] = True
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'


INTERNAL_IPS = ('127.0.0.1',)

USER_TIME_ZONE = 'Africa/Tunis'
LANGUAGE_CODE = 'fr-fr'
DEFAULT_LANGUAGE = "fr-fr"
DEFAULT_SMS_LANGUAGE = "fr-fr"
SECRET_KEY = 'abcddaslkldk;lsakdl;akdl;'

MAGE_API_URL = 'http://localhost:8026/api/v1'
MAGE_AUTH_TOKEN = 'ABCDEFGHIJKLMNOP'

TWITTER_API_KEY = '-'
TWITTER_API_SECRET = '-'

IP_ADDRESSES = ('192.168.60.2')

if TESTING:
    INSTALLED_APPS = INSTALLED_APPS + ('storages')
    MIDDLEWARE_CLASSES = ('temba.middleware.ExceptionMiddleware',) + MIDDLEWARE_CLASSES

    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    BROKER_BACKEND = 'memory'
else:
    CELERY_ALWAYS_EAGER = False
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    BROKER_BACKEND = 'redis'
ADMINS = (
    ('RapidPro', 'dwambua@ona.io'),
)
MANAGERS = ADMINS

# change for prod
EMAIL_HOST_USER = None
DEFAULT_FROM_EMAIL = None
EMAIL_HOST_PASSWORD = None
EMAIL_USE_TLS = True
EMAIL_HOST = None

# Attention: triggers actual messages and such
SEND_MESSAGES = not TESTING
SEND_WEBHOOKS = not TESTING
SEND_EMAILS = not TESTING

STATIC_ROOT = "/home/rapidpro/sitestatic"
COMPRESS_ROOT = STATIC_ROOT
MEDIA_ROOT = "/home/rapidpro/media"

DEFAULT_DOMAIN = ALLOWED_HOSTS[-1]
BRANDING_URL = "https://{}".format(DEFAULT_DOMAIN)
BRANDING = {
    'cims': {
        'slug': 'rapidpro',
        'name': 'RapidPro',
        'org': 'UNICEF',
        'styles': ['brands/rapidpro/font/style.css',
                   'brands/rapidpro/less/style.less'],
        'welcome_topup': 1000,
        'email': 'join@193.95.84.200',
        'support_email': 'support@rapidpro.ona.io',
        'link': BRANDING_URL,
        'api_link': BRANDING_URL,
        'docs_link': BRANDING_URL,
        'domain': DEFAULT_DOMAIN,
        'favico': 'brands/rapidpro/rapidpro.ico',
        'splash': '/brands/rapidpro/splash.jpg',
        'logo': '/brands/rapidpro/logo.png',
        'allow_signups': True,
        'tiers': dict(multi_user=0, multi_org=0),
        'bundles': [],
        'welcome_packs': [dict(size=5000, name="Demo Account"), dict(size=100000, name="UNICEF Account")],
        'description': "CIMS RapidPro",
        'credits': "Copyright &copy; 2012-2015 UNICEF, Nyaruka. All Rights Reserved.",
    }
}
DEFAULT_BRAND = 'cims'
