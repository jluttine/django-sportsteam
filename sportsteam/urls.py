from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.defaults import *

from django.conf import settings
from django.conf.urls.static import static

import teamstats.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^', include(teamstats.urls)),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# This enables the static files when developing and debugging
urlpatterns += staticfiles_urlpatterns()
