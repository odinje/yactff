from yactff.settings.base import *
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yactff.settings.production')

DEBUG = True

ALLOWED_HOSTS = ["web1.example.lan"]
INTERNAL_IPS = ["127.0.0.1"]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'myproject',
        'USER': 'myprojectuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}

BROKER_BACKEND = 'memory'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CTF_NAME = "Capture Tha Flag"
CTF_START = "2018-02-24 13:00:00"
CTF_END = "2018-02-24 14:10:00"
MAX_TEAM_SIZE = 5
CTF_FLAG_FORMAT = "ctf{...}"
