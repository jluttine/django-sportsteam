# Django settings for sportsteam project.

# DO NOT PUT ANY PRIVATE OR SYSTEM SPECIFIC SETTINGS HERE. USE ANOTHER SETTINGS
# FILE FOR THAT AND IMPORT EVERYTHING FROM HERE IN THAT FILE

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

TEAM_NAME = 'FC Team Name'
# This is the slug of the team name. It is used in URLs and email
# addresses etc. It should be in lower case, no whitespace, no special
# characters.
TEAM_SLUG = 'teamname'
# The tag used in email subject field as "[TEAM_TAG] Original subject"
TEAM_TAG = 'Team Name'

ADMINS = (
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'GMT'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

WSGI_APPLICATION = 'sportsteam.wsgi.application'

STATIC_URL = '/static/'
STATICFILES_DIRS = ( path('static/'), )
STATIC_ROOT = path('sitestatic/')

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# This will be deprecated in Django 1.4
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path('media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Make this unique, and don't share it with anybody.
# REDEFINE THIS IN LOCAL_SETTINGS.PY !
SECRET_KEY = 'jlfksd)(flT#tsdj9fasdft43_:sdg9034%Qdf!#vfsd'

# A list containing the settings for all template engines to be used with
# Django.
# https://docs.djangoproject.com/en/1.9/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [path('templates')],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
            ]
        }
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'sportsteam.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'teamstats',
)
