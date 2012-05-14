from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin



admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    # (r'^tuhlaajapojat/', include('tuhlaajapojat.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # (r'^(?P<season>\d+)/ottelut/$', 'tuhlaajapojat.views.ottelut'),

    (r'^ottelut/(?P<match_id>\d+)/$', 'tuhlaajapojat.views.ottelu'),

    (r'^kaudet/(?P<season_id>.+)/$', 'tuhlaajapojat.views.kausitilasto'),

    (r'^pelaajat/$', 'tuhlaajapojat.views.pelaajat'),

    (r'^pelaajat/(?P<player_id>.+)/$', 'tuhlaajapojat.views.pelaaja'),

    (r'^$', 'tuhlaajapojat.views.index'),

    

    # Uncomment the next line to enable the admin:
    #(r'^admin/stats/season/(?P<season_id>\d+)/match/add/$', 'tuhlaajapojat.stats.admin_views.add_match'),
    (r'^admin/', include(admin.site.urls)),
)

# This enables the static files when developing and debugging
#urlpatterns += staticfiles_urlpatterns()
