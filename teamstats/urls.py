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
from django.urls import path, re_path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from teamstats import views

#from teamstats.views import CalendarView

urlpatterns = [

    path(
        'ottelut/<int:match_id>/',
        views.show_match,
        name="show_match",
    ),
    path(
        'ottelut/(<int:match_id>/edit/',
        views.edit_match_result,
        name="edit_match_result",
    ),
    path(
        'kaudet/<str:season_id>/spl/',
        views.add_spl_matches,
        name="add_spl_matches",
    ),
    re_path(
        r'^kaudet/(?P<season_id>.+)/kalenteri-(?P=season_id).ics$',
        views.show_season_calendar,
        name="show_season_calendar",
    ),
    path(
        'kaudet/<str:season_id>/',
        views.show_season,
        name="show_season",
    ),
    path(
        'pelaajat/',
        views.show_all_players,
        name="show_all_players",
    ),
    path(
        'pelaajat/<str:player_id>/calendar/',
        views.show_player_calendar,
        name="show_player_calendar",
    ),
    path(
        'pelaajat/<str:player_id>/',
        views.show_player,
        name="show_player",
    ),
    path(
        'turnaukset/<str:name>/',
        views.show_tournament,
        name="show_tournament",
    ),
    path(
        'api/email/<str:list_name>/',
        views.get_mailing_list,
        name="get_mailing_list",
    ),
    path(
        r'',
        views.index,
        name="home",
    ),
]
