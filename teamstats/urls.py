from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin



admin.autodiscover()


urlpatterns = patterns('',

    (r'^ottelut/(?P<match_id>\d+)/$', 'sportsteam.views.ottelu'),

    (r'^kaudet/(?P<season_id>.+)/$', 'sportsteam.views.kausitilasto'),

    (r'^pelaajat/$', 'sportsteam.views.pelaajat'),

    (r'^pelaajat/(?P<player_id>.+)/$', 'sportsteam.views.pelaaja'),

    (r'^$', 'sportsteam.views.index'),
)

# This enables the static files when developing and debugging
#urlpatterns += staticfiles_urlpatterns()
