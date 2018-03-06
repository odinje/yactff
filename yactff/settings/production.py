from yactff.settings.base import *
import os
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yactff.settings.production')

DEBUG = False
COMPRESS_OFFLINE = True

try:
    with open(".key", "r") as f:
        SECRET_KEY = f.read()
except:
    with open(".key", "w") as f:
        SECRET_KEY = ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))
        f.write(SECRET_KEY)

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

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# CELERY SETTINGS
CTF_NAME = "Capture Tha Flag"
CTF_START = "2018-02-24 13:00:00"
CTF_END = "2018-02-24 14:10:00"
MAX_TEAM_SIZE = 5
CTF_FLAG_FORMAT = "ctf{...}"

