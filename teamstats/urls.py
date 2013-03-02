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

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',

    (r'^match/(?P<match_id>\d+)/$', 'teamstats.views.show_match'),

    (r'^season/(?P<season_id>.+)/$', 'teamstats.views.show_season'),

    (r'^player/$', 'teamstats.views.show_all_players'),

    (r'^player/(?P<player_id>.+)/$', 'teamstats.views.show_player'),

    (r'^$', 'teamstats.views.index'),
)
