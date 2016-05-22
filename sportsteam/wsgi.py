"""Configure WSGI file at: /etc/uwsgi/PROJECT_NAME.ini:

[uwsgi]
plugins = python
virtualenv = /path/to/virtualenv
env = DJANGO_SETTINGS_MODULE=sportsteam.settings.local
module = sportsteam.wsgi
uid = http
gid = http
vacuum = True

In this case, env setting is optional. wsgi.py has some default. Or ignore this
file:

[uwsgi]
plugins = python
virtualenv = /path/to/virtualenv
env = DJANGO_SETTINGS_MODULE=sportsteam.settings.local
module = django.core.wsgi:get_wsgi_application()
uid = http
gid = http
vacuum = True

"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'sportsteam.settings.default')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
