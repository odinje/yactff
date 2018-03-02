from yactff.settings.base import *
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yactff.settings.development')

DEBUG = True
COMPRESS_ENABLED = True
SECRET_KEY = '87k_d^98rd=b#h+c#%&+&+rjgq(+vmp31o12h67)1k@_#=f9ow'

ALLOWED_HOSTS = []
INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

BROKER_BACKEND = 'memory'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CTF_NAME = "Capture Tha Flag"
CTF_START = "2018-02-24 13:00:00"
CTF_END = "2018-02-24 14:10:00"
MAX_TEAM_SIZE = 5
CTF_FLAG_FORMAT = "dev{..}"
