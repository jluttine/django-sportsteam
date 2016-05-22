from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   path('sportsteam', 'sportsteam.sqlite'),
    }
}

INSTALLED_APPS = INSTALLED_APPS + (
    'django_extensions',
)
