from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    (r'^ottelut/(?P<match_id>\d+)/$', 'teamstats.views.ottelu'),

    (r'^kaudet/(?P<season_id>.+)/$', 'teamstats.views.kausitilasto'),

    (r'^pelaajat/$', 'teamstats.views.pelaajat'),

    (r'^pelaajat/(?P<player_id>.+)/$', 'teamstats.views.pelaaja'),

    (r'^$', 'teamstats.views.index'),
)
