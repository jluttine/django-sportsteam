# -*- coding: utf-8 -*-

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

"""
Views for showing different statistics of the team.
"""

from __future__ import division

from django.shortcuts import render_to_response, render, get_object_or_404
from django.template import RequestContext, Context, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Sum, Q
from django.core.urlresolvers import reverse
from itertools import chain
from django.conf import settings
from django.forms.formsets import formset_factory
from django.core.exceptions import PermissionDenied

from teamstats.models import *
from teamstats.forms import MatchPlayerForm, MatchChangeForm, SPLMatchAddForm

import caldav.views
from datetime import datetime, timedelta





def get_player_matches(player):
    """ Return all matches of a player. """
    return Match.objects.filter(season__players=player)



def index(request,
          league_class=League,
          template_name='teamstats/index.html'):
    '''
    View for the main page.
    '''
    context = {
        'league_list': league_class.objects.all(),
        'team_name':   settings.TEAM_NAME,
        }
    return render_to_response(template_name,
                              context)

def get_match_enrollments(match, 
                          seasonplayer_class=SeasonPlayer,
                          enrolledplayer_class=EnrolledPlayer):
    """
    Returns the enrollment statuses of the players.
    """
    # Show in/out stats
    seasonplayers = seasonplayer_class.objects.filter(season=match.season).order_by('player')
    # TODO: Use related_names and then just match.enrolledplayers
    enrollments = enrolledplayer_class.objects.filter(match=match).order_by('player__player')

    ind = 0
    enrolledplayers = []
    for player in seasonplayers:
        if ind < len(enrollments) and player.id == enrollments[ind].player.id:
            if enrollments[ind].enroll:
                player.choice = 1
            else:
                player.choice = 2
            ind = ind + 1
        else:
            player.choice = 3
        
        if player.choice == 1 or not player.passive:
            enrolledplayers.append(player)

    return enrolledplayers
    
def get_match_goals(match):
    if match.opponent_goals is not None:
        matchplayers = MatchPlayer.objects.filter(match=match)
        if not matchplayers:
            goals = match.opponent_owngoals
        else:
            goals = matchplayers.aggregate(Sum('goals')).values()[0] + match.opponent_owngoals
    else:
        goals = None

    return goals

def show_season(request, 
                season_id,
                season_class=Season,
                league_class=League,
                seasonplayer_class=SeasonPlayer,
                enrolledplayer_class=EnrolledPlayer,
                match_class=Match,
                template_name='teamstats/show_season.html'):
    '''
    View for showing information about a season: the players with
    statistics and all the matches.
    '''

    try:
        season = season_class.objects.get(id__exact=season_id)

        # Player stats
        player_list = seasonplayer_class.objects.filter(season=season)
        for player in player_list:
            matches = MatchPlayer.objects.filter(player=player)

            player.games = matches.count()
            player.goals = matches.aggregate(goals=Sum('goals')).values()[0]
            player.assists = matches.aggregate(assists=Sum('assists')).values()[0]
            
            if player.goals is None:
                player.goals = 0
            if player.assists is None:
                player.assists = 0

            player.points = player.goals + player.assists
            if player.games:
                player.ppg = player.points / player.games
            else:
                player.ppg = 0.0

                #season_list = season_class.objects.all()

        # TODO: Show opponent own goals!

        # Match list
        match_list = match_class.objects.filter(season=season)
        for match in match_list:
            match.goals = get_match_goals(match)
            match.result = (match.goals != None)
            if not match.result:
                match.player_list = get_match_enrollments(match,
                                                          seasonplayer_class=seasonplayer_class, 
                                                          enrolledplayer_class=enrolledplayer_class)
                match.player_list = sorted(match.player_list, 
                                           key=lambda player: player.player.shortname())
                match.player_list = sorted(match.player_list, 
                                           key=lambda player: player.choice)

        context = {
            'season':      season,
            'league_list': league_class.objects.all(),
            'match_list':  match_list,
            'player_list': player_list,
            'team_name':   settings.TEAM_NAME,
            }
        return render_to_response(template_name,
                                  context)

    except Season.DoesNotExist:
        return HttpResponse("Kautta ei olemassa.")


def show_all_players(request,
                     player_class=Player,
                     league_class=League,
                     matchplayer_class=MatchPlayer,
                     template_name='teamstats/show_all_players.html'):

    '''
    View for showing statistics for all the players.
    '''

    # Get all players
    player_list = player_class.objects.all()

    # Add player stats to the table one by one
    for player in player_list:
        matches = matchplayer_class.objects.filter(player__player=player)
        player.games = matches.count()
        player.goals = matches.aggregate(goals=Sum('goals')).values()[0]
        player.assists = matches.aggregate(assists=Sum('assists')).values()[0]
        if player.goals is None:
            player.goals = 0
        if player.assists is None:
            player.assists = 0
        player.points = player.goals + player.assists
        if player.games:
            player.ppg = player.points / player.games
        else:
            player.ppg = 0.0

    context = {
        'player_list': player_list,
        'league_list': league_class.objects.all(),
        'team_name': settings.TEAM_NAME,
        }

    return render_to_response(template_name,
                              context)

def show_match(request,
               match_id,
               match_class=Match,
               league_class=League,
               video_class=Video,
               seekpoint_class=SeekPoint,
               enrolledplayer_class=EnrolledPlayer,
               matchplayer_class=MatchPlayer,
               seasonplayer_class=SeasonPlayer,
               result_template_name='teamstats/show_match_result.html',
               registration_template_name='teamstats/show_match_registration.html'):

    '''
    View for showing information about a match. If the match has not
    yet been played, shows registrations of the players.  If the match
    has been played already, shows statistics of the players.
    '''

    try:
        match = match_class.objects.get(pk=match_id)

        video_list = video_class.objects.filter(match=match)
        for video in video_list:
            #video.mp4 = unicode(video.url)[:-4] + '.mp4'
            #video.ogg = unicode(video.url)[:-4] + '.ogg'
            #video.mp4 = video.url
            #video.ogg = video.url
            #video.mp4 = video.url[:-4] + '.mp4'
            #video.ogg = video.url[:-4] + '.ogg'
            video.seekpoint_list = seekpoint_class.objects.filter(video=video)

        match.goals = get_match_goals(match)
        result = (match.goals != None)
        match.played = result

        if result:
            # Print the result
            player_list = matchplayer_class.objects.filter(match=match)
            for player in player_list:
                player.points = player.goals + player.assists

            context = {
                'match':       match,
                'player_list': player_list,
                'video_list':  video_list,
                'league_list': league_class.objects.all(),
                'team_name':   settings.TEAM_NAME,
                }
            return render(request,
                          result_template_name,
                          context)
        else:
            # Match not played yet, show match enrollments
            
            # Register posted enrollment (if one is posted)
            try:
                post_input = request.POST['choice'].split('-')
                selected_player = int(post_input[0])
                selected_choice = int(post_input[1])
                try:
                    enroller = enrolledplayer_class.objects.get(match=match,
                                                                player__id=selected_player)
                    if selected_choice == 1 or selected_choice == 2:
                        enroller.enroll = (selected_choice == 1)
                        enroller.save()
                    else:
                        enroller.delete()
                except (enrolledplayer_class.DoesNotExist):
                    if selected_choice == 1 or selected_choice == 2:
                        player = seasonplayer_class.objects.get(id=selected_player)
                        enroller = enrolledplayer_class(match=match,
                                                        player=player,
                                                        enroll=(selected_choice==1))
                        enroller.save()
            except (KeyError):
                pass

            # Get a list of players with enrollment statuses
            players = sorted(get_match_enrollments(match,
                                                   seasonplayer_class=seasonplayer_class, 
                                                   enrolledplayer_class=enrolledplayer_class), 
                             key=lambda player: player.choice)

            context = {
                'player_list': players,
                'match':       match,
                'league_list': league_class.objects.all(),
                'team_name':   settings.TEAM_NAME,
                }
            return render(request,
                          registration_template_name,
                          context)

    except match_class.DoesNotExist:
        return HttpResponse("Ottelua ei olemassa.")

def show_player(request, 
                player_id,
                player_class=Player,
                match_class=Match,
                matchplayer_class=MatchPlayer,
                enrolledplayer_class=EnrolledPlayer,
                season_class=Season,
                seasonplayer_class=SeasonPlayer,
                league_class=League,
                template_name='teamstats/show_player.html'):

    '''
    View for showing information about a player.  Shows all the
    statistics for all the seasons the player has attended and lists
    all games the player has played in or can register in.
    '''
    
    try:
        # Get the player
        player = player_class.objects.get(pk=player_id)

        try:
            # Register enrollment (in/out/?) if one posted
            post_input = request.POST['choice'].split('-')
            selected_match = int(post_input[0])
            selected_choice = int(post_input[1])
            match = match_class.objects.get(id=selected_match)
            try:
                enroller = enrolledplayer_class.objects.get(match=match,
                                                            player__player=player)
                if selected_choice == 1 or selected_choice == 2:
                    enroller.enroll = (selected_choice == 1)
                    enroller.save()
                else:
                    enroller.delete()
            except (enrolledplayer_class.DoesNotExist):
                if selected_choice == 1 or selected_choice == 2:
                    seasonplayer = seasonplayer_class.objects.get(season=match.season,
                                                                  player=player)
                    enroller = enrolledplayer_class(match=match,
                                                    player=seasonplayer,
                                                    enroll=(selected_choice==1))
                    enroller.save()
        except (KeyError, match_class.DoesNotExist):
            pass

        # TODO: Use related_names and remove this!
        season_list = season_class.objects.all()

        total_games = 0
        total_goals = 0
        total_assists = 0
        total_points = 0

        # TODO: Use related_names to get the code cleaner!
        seasonplayer_list = []
        for season in season_list:
            try:
                seasonplayer = seasonplayer_class.objects.get(season=season,
                                                              player=player)
                matchplayers = matchplayer_class.objects.filter(player=seasonplayer,
                                                                match__opponent_goals__isnull=False)
                #enrolledplayers = EnrolledPlayer.objects.filter(player=seasonplayer)

                for matchplayer in matchplayers:
                    matchplayer.match.result = True
                    matchplayer.match.goals = matchplayer_class.objects.filter(match=matchplayer.match).aggregate(Sum('goals')).values()[0] + matchplayer.match.opponent_owngoals

                enrolledplayers = list()
                
                if seasonplayer_class.objects.filter(season=season,
                                                     player=player,
                                                     passive=False).exists():
                    matches = match_class.objects.filter(season=season,
                                                         opponent_goals__isnull=True)
                else:
                    matches = []

                for match in matches:
                    match.result = False
                    try:
                        enrolledplayer = enrolledplayer_class.objects.get(match=match,
                                                                          player=seasonplayer)
                        if enrolledplayer.enroll:
                            enrolledplayer.choice = 1
                        else:
                            enrolledplayer.choice = 2
                    except (enrolledplayer_class.DoesNotExist):
                        enrolledplayer = enrolledplayer_class(match=match,
                                                              player=seasonplayer,
                                                              enroll=True)
                        enrolledplayer.choice = 3
                    enrolledplayers.append(enrolledplayer)

                seasonplayer.matchplayer_list = list(chain(matchplayers, 
                                                           enrolledplayers))

                # Compute season statistics
                games = matchplayers.count()
                goals = matchplayers.aggregate(Sum('goals')).values()[0]
                assists = matchplayers.aggregate(Sum('assists')).values()[0]
                if goals is None:
                    goals = 0
                if assists is None:
                    assists = 0
                points = goals + assists

                # Add season stats to total stats
                total_games += games
                total_goals += goals
                total_assists += assists
                total_points += points

                # Add season stats
                seasonplayer.games = games
                seasonplayer.goals = goals
                seasonplayer.assists = assists
                seasonplayer.points = goals + assists
                if games:
                    seasonplayer.ppg = seasonplayer.points / games
                else:
                    seasonplayer.ppg = 0.0
                
                seasonplayer_list.append(seasonplayer)

            except seasonplayer_class.DoesNotExist:
                pass

        # Add total stats
        player.games = total_games
        player.goals = total_goals
        player.assists = total_assists
        player.points = total_points
        if total_games:
            player.ppg = total_points / total_games
        else:
            player.ppg = 0.0

        context = {
            'player':            player,
            'seasonplayer_list': seasonplayer_list,
            'league_list':       league_class.objects.all(),
            'team_name':         settings.TEAM_NAME,
            }
        return render(request,
                      template_name,
                      context)
    except player_class.DoesNotExist:
        return HttpResponse("Pelaajaa ei olemassa.")


def show_player_calendar(request, 
                         player_id,
                         player_class=Player,
                         match_class=Match,
                         matchplayer_class=MatchPlayer,
                         enrolledplayer_class=EnrolledPlayer,
                         season_class=Season,
                         seasonplayer_class=SeasonPlayer,
                         league_class=League,
                         template_name='teamstats/show_player.html'):

    """
    Show player's match calendar.
    """

    print("Kalenteria kysellaan")
    print(request.GET)
    print(request.method)
    print(request.body)
    print(request.OPTIONS.dict())
    #print(request.META)
    
    # Get the player
    try:
        player = player_class.objects.get(pk=player_id)
    except player_class.DoesNotExist:
        return HttpResponse("Pelaajaa ei olemassa.")

    
    matches = get_player_matches(player)

    events = (caldav.views.create_event(uid=str(match.id),
                                        summary='%s: %s' % (match.season.league, match.opponent),
                                        description=request.build_absolute_uri(reverse('show_match', kwargs={'match_id': match.id})),
                                        url=request.build_absolute_uri(reverse('show_match', kwargs={'match_id': match.id})),
                                        dtstart=match.date,#caldav.views.date(match.date),
                                        #dtend=match.date+timedelta(hours=1),#caldav.views.enddate(match.date),
                                        location=match.field)
              for match in matches)

    return HttpResponse(caldav.views.events(events))


def show_season_calendar(request, 
                         season_id,
                         player_class=Player,
                         match_class=Match,
                         matchplayer_class=MatchPlayer,
                         enrolledplayer_class=EnrolledPlayer,
                         season_class=Season,
                         seasonplayer_class=SeasonPlayer,
                         league_class=League,
                         template_name='teamstats/show_player.html'):

    """
    Show match calendar of a season.
    """

    # Get the season
    season = get_object_or_404(season_class, pk=season_id)

    # Get the matches in the season
    matches = match_class.objects.filter(season=season)

    events = (caldav.views.create_event(uid=str(match.id),
                                        summary='%s: %s' % (match.season.league, match.opponent),
                                        description=request.build_absolute_uri(reverse('show_match', kwargs={'match_id': match.id})),
                                        url=request.build_absolute_uri(reverse('show_match', kwargs={'match_id': match.id})),
                                        dtstart=match.date,#caldav.views.date(match.date),
                                        #dtend=match.date+timedelta(hours=1),#caldav.views.enddate(match.date),
                                        location=match.field)
              for match in matches)

    return HttpResponse(caldav.views.events(events))


def edit_match_result(request, match_id,
                      league_class=League,
                      template_name="teamstats/edit_match_result.html"):

    if not request.user.is_authenticated():
        raise PermissionDenied

    # You could check some permissions in more detail:
    #add: user.has_perm('foo.add_bar')
    #change: user.has_perm('foo.change_bar')
    #delete: user.has_perm('foo.delete_bar')

    #form = MatchChangeForm

    try:
        match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        raise Http404
    
    players = SeasonPlayer.objects.filter(season=match.season)

    PlayerFormSet = formset_factory(MatchPlayerForm, 
                                    extra=len(players))

    
    valid_save = False

    if request.method == 'POST':
        cancel = request.POST.get('cancel', None)
        if cancel:
            return HttpResponseRedirect(reverse('show_match', 
                                                args=(match_id,)))
                                                
        match_form = MatchChangeForm(request.POST, instance=match)
        player_formset = PlayerFormSet(request.POST)
        if player_formset.is_valid():
            # Save the valid player+number information
            valid_save = True
            for (player,form) in zip(players, player_formset):
                played = form.cleaned_data['played']
                goals = form.cleaned_data['goals']
                assists = form.cleaned_data['assists']
                try:
                    matchplayer = MatchPlayer.objects.get(match=match,
                                                          player=player)
                    if played:
                        # Modify existing match player
                        matchplayer.goals = goals
                        matchplayer.assists = assists
                        matchplayer.save()
                    else:
                        # Delete the match player because he did not play
                        matchplayer.delete()
                except MatchPlayer.DoesNotExist:
                    if played:
                        # Create a new match player
                        matchplayer = MatchPlayer(match=match, 
                                                  player=player,
                                                  goals=goals,
                                                  assists=assists)
                        matchplayer.save()

            match_form.save()
            return HttpResponseRedirect(reverse('show_match', 
                                                args=(match_id,)))
                        
    # Initialize formset with existing game stats
    if not valid_save:
        match_form = MatchChangeForm(instance=match)
        player_formset = PlayerFormSet()
        for (player, form) in zip(players, player_formset):
            try:
                matchplayer = MatchPlayer.objects.get(match=match,
                                                      player=player)
                played = True
                goals = matchplayer.goals
                assists = matchplayer.assists
            except MatchPlayer.DoesNotExist:
                played = False
                goals = 0
                assists = 0
            form.fields['played'].initial = played
            form.fields['goals'].initial = goals
            form.fields['assists'].initial = assists
            
    # Add player information into the forms
    for (form, player) in zip(player_formset.forms, players):
        form.player = player

    context = {
        'match_form': match_form,
        'player_formset': player_formset,
        'league_list': league_class.objects.all(),
        'team_name':   settings.TEAM_NAME,
    }

    return render(request,
                  template_name,
                  context)

def add_spl_matches(request, season_id,
                    template_name="teamstats/add_spl_matches.html"):

    if not request.user.is_authenticated():
        raise PermissionDenied

    # You could check some permissions in more detail:
    #add: user.has_perm('foo.add_bar')
    #change: user.has_perm('foo.change_bar')
    #delete: user.has_perm('foo.delete_bar')

    try:
        season = Season.objects.get(id=season_id)
    except Season.DoesNotExist:
        raise Http404
    
    if request.method == 'POST':
        cancel = request.POST.get('cancel', None)
        if cancel:
            return HttpResponseRedirect(reverse('show_season', 
                                                args=(season_id,)))
        
        matches_form = SPLMatchAddForm(season, request.POST)
        if matches_form.is_valid():
            matches_form.save(season)
            return HttpResponseRedirect(reverse('show_season', 
                                                args=(season_id,)))
    else:
        matches_form = SPLMatchAddForm(season)
                        
    context = {
        'matches_form': matches_form,
        'league_list':  League.objects.all(),
        'team_name':    settings.TEAM_NAME,
    }

    return render(request,
                  template_name,
                  context)
    
    


from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseBadRequest
from django_caldav.views import CalDavView, CalDavFeedView
from django.shortcuts import get_object_or_404
#from example.our_calendar.models import OurCalendarEvent


class CalendarFeedView(CalDavFeedView):
    product_id = '-//example.com//Example//EN'
    timezone = 'UTC'
    now = datetime.now()
    #min_date = now + timedelta(days=-7)
    #max_date = now + timedelta(days=14)


    ## def get_object(self, request):
    ## #def get_object(self, request, player_id):
    ##     print("GETTING OBJECT")
    ##     return None
    ##     return get_object_or_404(Player, id=player_id)


    def items(self):
    #def items(self, player):
        return Match.objects.all() #filter(season__players=player)
        #return Match.objects.filter(season__players=player)


    def item_title(self, match):
        return "%s: %s" % (match.season.league, match.opponent)


    def item_description(self, match):
        return "TODO"


    def item_start_datetime(self, match):
        return match.date


    def item_end_datetime(self, match):
        return match.date + timedelta(hours=1)


    def item_location(self, match):
        return match.field


    def item_link(self, match):
        return "TODO" #"/{pk}.ics".format(pk=item.pk)


    ## def item_save(self, request, base_item, iCalendar_component, *args, **kwargs):
    ##     return HttpResponseBadRequest()




from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
class CalendarView(CalDavView):
    """
    A simple event calender
    """
    feed_view = CalendarFeedView

    @method_decorator(csrf_exempt)
    def dispatch(self, request, path, *args, **kwargs):
        print("IN DISPATCH YEY!")
        retval = super(CalendarView, self).dispatch(request, path, *args, **kwargs)
        #print("REQUEST")
        #print(request)
        print("RESPONSE")
        print(retval)
        if not retval:
            print("RESPONSE EMPTY")
        return retval


