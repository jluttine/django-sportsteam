# -*- encoding: utf-8 -*- 

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
from django.conf import settings
import datetime

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
        
class SPLMatchAddForm(forms.Form):
    """
    Form for inputting match data from SPL.
    """

    """ A field for adding several matches """
    year = forms.IntegerField()
    matches = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 
                                                           'rows': 30}))

    def __init__(self, season, *args, **kwargs):
        self.season = season
        super(SPLMatchAddForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        The format:

        ### day.month. <TAB> hour:minute <TAB> field <TAB> home <TAB> visitor <TAB> xxx
        """
        cleaned_data = super(SPLMatchAddForm, self).clean()
        if any(self.errors):
            return cleaned_data

        lines = cleaned_data['matches'].split("\n")

        matches = []
        for line in lines:
            if len(line) > 0:
                cols = line.split("\t")
                datestr = '%s%d %s' % (cols[0].strip(), 
                                       cleaned_data['year'],
                                       cols[1].strip())
                date = datetime.datetime.strptime(datestr, "%d.%m.%Y %H:%M")
                try:
                    field = Field.objects.get(name=cols[2].strip())
                except Field.DoesNotExist:
                    raise forms.ValidationError(u"Tuntematon kenttä '%s'" 
                                                % cols[2].strip())
                home = cols[3].strip()
                visitor = cols[4].strip()
                if home == settings.TEAM_NAME:
                    opponent = visitor
                    is_home = True
                elif visitor == settings.TEAM_NAME:
                    opponent = home
                    is_home = False
                else:
                    raise forms.ValidationError("Oma joukkue ei pelaa ottelussa")
                print(date, field, opponent, is_home)
                match = Match(season=self.season,
                              date=date,
                              opponent=opponent,
                              field=field,
                              home=is_home)
                matches.append(match)

        for match in matches:
            match.save()
        
        return cleaned_data

    def save(self, season):
        pass



