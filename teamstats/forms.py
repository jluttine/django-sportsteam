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

from django import forms
from teamstats.models import *

## class SeasonChangeForm(forms.ModelForm):
##     class Meta:
        

class MatchAddForm(forms.ModelForm):
    class Meta:
        model = Match
        exclude = ('opponent_goals', 'opponent_owngoals',)

class MatchChangeForm(forms.ModelForm):
    class Meta:
        model = Match
        exclude = ('season','players','opponent','date','home','field',)
        #include = ('opponent_goals', 'opponent_owngoals',)

class MatchPlayerForm(forms.Form):
    #player = ""
    played = forms.BooleanField(required=False)
    goals = forms.IntegerField()
    assists = forms.IntegerField()

class SeasonPlayerForm(forms.ModelForm):
    player = forms.CharField(max_length=100)
    #number = forms.IntegerField(required=False)
    class Meta:
        model = SeasonPlayer
        exclude = ('season',)

## class SeasonPlayerForm(forms.Form):
##     player = ""
##     number = forms.IntegerField(required=False)


