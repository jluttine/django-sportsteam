
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from sportsteam.teamstats.models import *
from django.contrib import admin

from sportsteam.teamstats.admin import MatchAdmin

# TODO: IS THIS FILE USED??

def add_match(request, season_id):
    match_admin = MatchAdmin(Match,admin.site)
    return match_admin.add_view(request, season_id)

