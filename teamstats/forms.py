from django import forms
from teamstats.models import *

class MatchAddForm(forms.ModelForm):
    class Meta:
        model = Match
        exclude = ('opponent_goals', 'opponent_owngoals',)

class MatchChangeForm(forms.ModelForm):
    class Meta:
        model = Match
        exclude = ('season',)

class MatchPlayerForm(forms.Form):
    player = ""
    played = forms.BooleanField(required=False)
    goals = forms.IntegerField()
    assists = forms.IntegerField()

class SeasonPlayerForm(forms.Form):
    player = ""
    number = forms.IntegerField(required=False)


