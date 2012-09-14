from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.defaults import *

from sportsteam import teamstats

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^/$', include(teamstats.urls)),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

)

# This enables the static files when developing and debugging
#urlpatterns += staticfiles_urlpatterns()
