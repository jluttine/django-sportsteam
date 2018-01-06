from sportsteam.settings.base import *

# A helpful function to avoid writing absolute paths
import os
path = lambda *args: os.path.join(
    os.path.abspath(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    __file__
                )
            )
        )
    ),
    *args
)

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   path('sportsteam', 'sportsteam.sqlite'),
    }
}

INSTALLED_APPS = INSTALLED_APPS + (
    #'django_extensions',
)
