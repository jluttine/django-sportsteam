from teamstats.models import *
from teamstats.forms import *
from django.contrib import admin

class SeekPointInline(admin.TabularInline):
    model = SeekPoint
    extra = 15

class VideoAdmin(admin.ModelAdmin):
    inlines = [SeekPointInline]

class MatchPlayerInline(admin.TabularInline):
    model = MatchPlayer
    extra = 12
    form = MatchPlayerForm

class MatchAdmin(admin.ModelAdmin):

    change_form_template = "admin/stats/match_change_form.html"

    form = MatchAddForm

    def add_view(self, request, form_url='', extra_context=None):

        if not self.has_add_permission(request):
            raise PermissionDenied

        self.form = MatchAddForm
        
        return super(MatchAdmin, self).add_view(request, form_url,
                                                extra_context)

    def change_view(self, request, object_id, extra_context=None):

        if not self.has_add_permission(request):
            raise PermissionDenied
        
        self.form = MatchChangeForm

        match = Match.objects.get(id=object_id)
        players = SeasonPlayer.objects.filter(season__id__exact=match.season.id)

        PlayerFormSet = forms.formsets.formset_factory(MatchPlayerForm, extra=0)

        valid_save = False
        
        if request.method == 'POST':
            player_formset = PlayerFormSet(request.POST, request.FILES)
            if player_formset.is_valid():
                # Save the valid player+number information
                valid_save = True
                for (player,form) in zip(players, player_formset.cleaned_data):
                    played = form['played']
                    goals = form['goals']
                    assists = form['assists']
                    # Delete all existing players of the season
                    try:
                        matchplayer = MatchPlayer.objects.filter(match__id__exact=object_id).get(player=player)
                        matchplayer.delete()
                    except MatchPlayer.DoesNotExist:
                        pass
                    # Add the new player to the match
                    if played:
                        matchplayer = MatchPlayer(match=match, player=player, goals=goals, assists=assists)
                        matchplayer.save()
            else:
                print player_formset.errors

        # Initialize formset with existing game stats
        if not valid_save:
            allplayed = []
            allgoals = []
            allassists = []
            for player in players:
                try:
                    matchplayer = MatchPlayer.objects.filter(match__id__exact=object_id).get(player=player)
                    played = True
                    goals = matchplayer.goals
                    assists = matchplayer.assists
                except MatchPlayer.DoesNotExist:
                    played = False
                    goals = 0
                    assists = 0
                allplayed.append(played)
                allgoals.append(goals)
                allassists.append(assists)
            player_formset = PlayerFormSet(initial=[{'played':played, 'goals': goals, 'assists': assists} for (played,goals,assists) in zip(allplayed,allgoals,allassists)])

        # Add player information into the forms
        for (form, player) in zip(player_formset.forms, players):
            form.player = player
            print player

        my_context = {
            'player_formset': player_formset,
        }

        return super(MatchAdmin, self).change_view(request, object_id, my_context)

    
class SeasonAdmin(admin.ModelAdmin):
    change_form_template = "admin/stats/season_change_form.html"
    
    def change_view(self, request, object_id, extra_context=None):

        if not self.has_add_permission(request):
            raise PermissionDenied

        players = Player.objects.all()
        PlayerFormSet = forms.formsets.formset_factory(SeasonPlayerForm, extra=0)

        valid_save = False
        
        if request.method == 'POST':
            player_formset = PlayerFormSet(request.POST, request.FILES)
            if player_formset.is_valid():
                # Save the valid player+number information
                valid_save = True
                for (player,form) in zip(players, player_formset.cleaned_data):
                    number = form['number']
                    # Delete all existing players of the season
                    try:
                        seasonplayer = SeasonPlayer.objects.filter(season__id__exact=object_id).get(player=player)
                        seasonplayer.delete()
                    except SeasonPlayer.DoesNotExist:
                        pass
                    # Add the new players to the season
                    if number is not None:
                        season = Season.objects.get(id=object_id)
                        seasonplayer = SeasonPlayer(season=season, player=player, number=number)
                        seasonplayer.save()
            else:
                print player_formset.errors

        # Initialize formset with existing numbers
        if not valid_save:
            numbers = []
            for player in players:
                try:
                    seasonplayer = SeasonPlayer.objects.filter(season__id__exact=object_id).get(player=player)
                    number = seasonplayer.number
                except SeasonPlayer.DoesNotExist:
                    number = None
                numbers.append(number)
            player_formset = PlayerFormSet(initial=[{'number': n} for n in numbers])

        # Add player information into the forms
        for (form, player) in zip(player_formset.forms, players):
            form.player = player

        my_context = {
            #'players': players,
            'player_formset': player_formset,
        }
        return super(SeasonAdmin, self).change_view(request, object_id, my_context)
    

admin.site.register(Player)
admin.site.register(Field)
admin.site.register(Match, MatchAdmin)
#admin.site.register(Match, MatchResultAdmin)
#admin.site.register(MatchPlayer)
#admin.site.register(Season, SeasonAdmin) # Custom season form
admin.site.register(Season)
admin.site.register(SeasonPlayer)
admin.site.register(Video, VideoAdmin)
admin.site.register(League)
#admin.site.register(SeekPoint)
