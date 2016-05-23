# Copyright (C) 2011,2012 Jaakko Luttinen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

#from django.conf.urls.defaults import *
from django.conf.urls import url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from teamstats import views

#from teamstats.views import CalendarView

urlpatterns = [

    url(r'^ottelut/(?P<match_id>\d+)/$',
        views.show_match,
        name="show_match"),

    url(r'^ottelut/(?P<match_id>\d+)/edit/$',
        views.edit_match_result,
        name="edit_match_result"),

    url(r'^kaudet/(?P<season_id>.+)/spl/$',
        views.add_spl_matches,
        name="add_spl_matches"),

    url(r'^kaudet/(?P<season_id>.+)/kalenteri-(?P=season_id).ics$',
        views.show_season_calendar,
        name="show_season_calendar"),

    url(r'^kaudet/(?P<season_id>.+)/$',
        views.show_season,
        name="show_season"),

    url(r'^pelaajat/$',
        views.show_all_players,
        name="show_all_players"),

    url(r'^pelaajat/(?P<player_id>.+)/calendar/$',
        views.show_player_calendar,
        name="show_player_calendar"),

    url(r'^pelaajat/(?P<player_id>.+)/$',
        views.show_player,
        name="show_player"),

    url(r'^api/email/(?P<list_name>.+)/$',
        views.get_mailing_list,
        name="get_mailing_list"),

    url(r'^$',
        views.index,
        name="home"),

]
