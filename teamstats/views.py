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
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.db.models import Sum, Q, Avg, Count, F, Value, BooleanField, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.core.urlresolvers import reverse
from itertools import chain
from django.conf import settings
from django.forms.formsets import formset_factory
from django.core.exceptions import PermissionDenied
from django.utils import timezone

import json

import numpy as np

from teamstats.models import *
from teamstats.forms import MatchPlayerForm, MatchChangeForm, SPLMatchAddForm, TournamentMatchResultForm

import caldav.views
from datetime import datetime, timedelta


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
    except season_class.DoesNotExist:
        return Http404()

    player_list = (
        seasonplayer_class.objects
        .filter(season=season_id)
        .annotate_stats()
    )

    # TODO: Show opponent own goals!

    # Season matches
    match_list = (
        match_class.objects
        .filter(season=season_id)
        .annotate_result()
        .annotate_enrollments(player_list)
    )

    context = {
        'season':      season,
        'league_list': league_class.objects.all(),
        'match_list':  match_list,
        'player_list': player_list,
        'team_name':   settings.TEAM_NAME,
    }

    return render_to_response(template_name, context)


def show_all_players(request,
                     player_class=Player,
                     league_class=League,
                     matchplayer_class=MatchPlayer,
                     template_name='teamstats/show_all_players.html'):

    '''
    View for showing statistics for all the players.
    '''

    player_list = player_class.objects.annotate_stats()

    context = {
        'player_list': player_list,
        'league_list': league_class.objects.all(),
        'team_name': settings.TEAM_NAME,
    }

    return render_to_response(template_name, context)

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
        match = (
            match_class.objects
            .annotate_result()
            .get(pk=match_id)
        )
    except match_class.DoesNotExist:
        raise Http404()

    video_list = video_class.objects.filter(match=match)
    for video in video_list:
        #video.mp4 = unicode(video.url)[:-4] + '.mp4'
        #video.ogg = unicode(video.url)[:-4] + '.ogg'
        #video.mp4 = video.url
        #video.ogg = video.url
        #video.mp4 = video.url[:-4] + '.mp4'
        #video.ogg = video.url[:-4] + '.ogg'
        video.seekpoint_list = seekpoint_class.objects.filter(video=video)

    if match.result:
        # Print the result
        player_list = (
            matchplayer_class.objects
            .annotate_points()
            .filter(match=match)
        )

        context = {
            'match':       match,
            'player_list': player_list,
            'video_list':  video_list,
            'league_list': league_class.objects.all(),
            'team_name':   settings.TEAM_NAME,
            }

        return render(request, result_template_name, context)

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

        return render(request, registration_template_name, context)


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

    # Get the player
    try:
        player = (
            player_class.objects
            .annotate_stats()
            .get(pk=player_id)
        )
    except player_class.DoesNotExist:
        raise Http404()

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

    seasonplayer_list = (
        seasonplayer_class.objects
        .annotate_stats()
        .filter(player=player)
    )

    active_seasons = [
        seasonplayer.season
        for seasonplayer in seasonplayer_list
        if not seasonplayer.passive
    ]

    #
    # Fetch all matches the player has played
    #

    matchplayers = (
        MatchPlayer.objects
        .filter(
            player__player=player,
            match__opponent_goals__isnull=False,
        )
        .prefetch_related("match")
        .annotate(
            match_goals=Sum("match__matchplayer__goals") + F("match__opponent_owngoals"),
        )
    )

    def get_annotated_match(matchplayer):
        match = matchplayer.match
        match.result = True
        match.goals = matchplayer.match_goals
        match.player_goals = matchplayer.goals
        match.player_assists = matchplayer.assists
        return match

    played_matches = [get_annotated_match(matchplayer) for matchplayer in matchplayers]


    #
    # Fetch enrolled matches
    #

    enrolledplayers = (
        EnrolledPlayer.objects
        .filter(
            player__player=player,
            match__opponent_goals__isnull=True,
        )
        .prefetch_related("match")
    )

    def get_annotated_enrolled_match(enrolledplayer):
        match = enrolledplayer.match
        match.player_enrolled = enrolledplayer.enroll
        return match

    enrolled_matches = [
        get_annotated_enrolled_match(enrolledplayer)
        for enrolledplayer in enrolledplayers
    ]


    #
    # Upcoming not-enrolled matches
    #
    upcoming_matches = (
        Match.objects
        .filter(
            season__in=active_seasons,
            opponent_goals__isnull=True,
        )
        .exclude(
            enrolledplayer__player__player=player,
        )
    )


    #
    # Merge three match lists and sort
    #

    match_list = sorted(
        list(played_matches) + list(enrolled_matches) + list(upcoming_matches),
        key=lambda x: (x.season, x.date)
    )

    context = {
        'player':            player,
        'seasonplayer_list': seasonplayer_list,
        'match_list':        match_list,
        'league_list':       league_class.objects.all(),
        'team_name':         settings.TEAM_NAME,
        }
    return render(request,
                    template_name,
                    context)


def get_mailing_list(request, list_name):

    def to_json(tag, emails):
        # return HttpResponse(
        #     json.dumps(dict(emails=emails, tag=tag), ensure_ascii=False),
        #     content_type="application/json; charset=utf-8"
        # )
        return JsonResponse(
            dict(emails=emails, tag=tag),
            json_dumps_params=dict(ensure_ascii=False),
        )

    if list_name.lower() == 'webmaster':
        emails = [admin[1] for admin in settings.ADMINS]
        return to_json(
            emails=emails,
            tag='[{0}-Webmaster]'.format(settings.TEAM_TAG)
        )

    # Try if for everyone
    if list_name.lower() == settings.TEAM_SLUG:
        players = Player.objects.all()
        emails = [player.email for player in players if player.email]
        return to_json(
            emails=emails,
            tag='[{0}]'.format(settings.TEAM_TAG)
        )

    # Try matching to full season IDs
    try:
        season = Season.objects.get(id__iexact=list_name)
    except Season.DoesNotExist:
        pass
    else:
        players = SeasonPlayer.objects.filter(season__id=season.id,passive=False)
        emails = [player.player.email for player in players]
        return to_json(
            emails=emails,
            tag='[{0}-{1}]'.format(settings.TEAM_TAG, season.league)
        )

    # Try matching to player IDs
    try:
        player = Player.objects.get(id__iexact=list_name)
    except Player.DoesNotExist:
        pass
    else:
        return to_json(
                emails=[player.email] if player.email else None,
                tag=''
        )

    # No match
    return to_json(
        emails=None,
        tag=''
    )


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

    tz = timezone.get_default_timezone()

    events = (caldav.views.create_event(uid=str(match.id),
                                        summary='%s: %s' % (match.season.league, match.opponent),
                                        description=request.build_absolute_uri(reverse('show_match', kwargs={'match_id': match.id})),
                                        url=request.build_absolute_uri(reverse('show_match', kwargs={'match_id': match.id})),
                                        dtstart=match.date.astimezone(tz),#caldav.views.date(match.date),
                                        #dtend=match.date+timedelta(hours=1),#caldav.views.enddate(match.date),
                                        location=match.field)
              for match in matches)

    return HttpResponse(caldav.views.events(events), content_type="text/calendar")


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


def show_tournament(request, name):

    tournament = get_object_or_404(Tournament, name=name)

    players = list(
        TournamentPlayer.objects
        # .prefetch_related('home_match')
        # .prefetch_related('away_match')
        .filter(tournament=tournament)
        .annotate(
            games=Count("player__seasonplayer__matchplayer"),
            goals=Coalesce(
                Sum("player__seasonplayer__matchplayer__goals"),
                Value(0),
            ),
            assists=Coalesce(
                Sum("player__seasonplayer__matchplayer__assists"),
                Value(0),
            ),
        )
        .annotate(
            points=F("goals") + F("assists"),
        )
        .annotate(
            ppg=PPG_ANNOTATION,
        )
        .annotate(
            # Django doesn't support annotations over multiple tables, thus we
            # need to use Subquery. And that needs to be run *after* the normal
            # annotations..
            tournament_points=(
                Coalesce(
                    Subquery(
                        TournamentPlayer.objects
                        .filter(id=OuterRef("pk"))
                        .annotate(sum=Sum("home_match__home_goals"))
                        .values("sum")
                    ),
                    Value(0)
                ) + Coalesce(
                    Subquery(
                        TournamentPlayer.objects
                        .filter(id=OuterRef("pk"))
                        .annotate(sum=Sum("away_match__away_goals"))
                        .values("sum")
                    ),
                    Value(0)
                )
            )
        )
        .order_by("-tournament_points", "-ppg")
        # .prefetch_related('home_match')
        # .prefetch_related('away_match')
    )

    # players2 = (
    #     players
    #     .annotate(
    #         **{
    #             "with_{0}".format(ind):
    #             Subquery(
    #                 TournamentMatch.objects
    #                 .filter(home_team=OuterRef("pk"))
    #                 .filter(home_team=player)
    #                 .count()
    #             ) + Subquery(
    #                 TournamentMatch.objects
    #                 .filter(away_team=OuterRef("pk"))
    #                 .filter(away_team=player)
    #                 .count()
    #             )
    #             for (ind, player) in enumerate(list(players))
    #         }
    #     )
    # )

    matches = TournamentMatch.objects.filter(tournament=tournament)

    #
    # Construct a matrix of how many times players have been in the same team
    #
    N = len(players)
    counts = np.zeros((N, N))
    ids = {player.id: ind for (ind, player) in enumerate(players)}
    for match in matches:
        for team in (match.home_team, match.away_team):
            ps = team.all()
            for a in ps:
                for b in ps:
                    i = ids[a.id]
                    j = ids[b.id]
                    counts[i,j] = counts[i,j] + 1

    #
    # Form next teams
    #

    # Captains
    #   A <- the best player
    #   B <- the best player that has played the most with captain A

    def pop_player(players, ind):
        return (players[ind], players[:ind] + players[(ind+1):])

    remaining_players = players
    (captain_A, remaining_players) = pop_player(
        remaining_players,
        0
    )
    (captain_B, remaining_players) = pop_player(
        remaining_players,
        np.argmax(counts[0,1:])
    )

    # In turns, add to each team a player that has played the least with any of
    # the players in the team

    def foobar(team, other_team, remaining_players):

        if len(remaining_players) == 0:
            return (team, other_team)

        # Uneven amount of players
        if len(remaining_players) == 1 and (len(team) + len(other_team)) % 2 == 0:
            # Add the last player to the other team just to even out the
            # balance
            return (team, other_team + remaining_players)

        rows = [ids[player.id] for player in team]
        columns = [ids[player.id] for player in remaining_players]

        # Sort by common match counts
        c = np.sort(counts[np.ix_(rows, columns)], axis=0)[::-1,:]

        # Choose player with least common games
        ind = np.lexsort(c)[0]
        (chosen_player, remaining_players) = pop_player(
            remaining_players,
            ind
        )
        (b, a) = foobar(
            other_team,
            team + [chosen_player],
            remaining_players,
        )
        # Switch the order of the teams back :)
        return (a, b)

    (home_team, away_team) = foobar(
        [captain_A],
        [captain_B],
        # Reverse order so "worse" players are preferred when match counts are
        # tied
        remaining_players[::-1],
    )

    if request.method == 'POST':
        if request.POST.get('delete', None):
            last_match = TournamentMatch.objects.all().last()
            if last_match is not None:
                last_match.delete()
            return HttpResponseRedirect(
                reverse('show_tournament', args=(name,))
            )
        elif request.POST.get('save', None):
            # Save match result
            result_form = TournamentMatchResultForm(
                tournament,
                home_team,
                away_team,
                request.POST,
            )
            if result_form.is_valid():
                result_form.save()
                return HttpResponseRedirect(
                    reverse('show_tournament', args=(name,))
                )

    result_form = TournamentMatchResultForm(tournament, home_team, away_team)

    matches = TournamentMatch.objects.filter(tournament=tournament)
    match_count = matches.count()

    def add(x, y):
        return (
            x if y is None else
            y if x is None else
            x + y
        )

    match_points = [
        [
            add(
                (
                    match.home_goals
                    if player in match.home_team.all() else
                    None
                ),
                (
                    match.away_goals
                    if player in match.away_team.all() else
                    None
                )
            )
            for match in matches
        ]
        for player in players
    ]

    for (player, p) in zip(players, match_points):
        player.match_points = p

    context = {
        "tournament":   tournament,
        "tournamentplayers":       players,
        "home_team": home_team,
        "away_team": away_team,
        "result_form": result_form,
        "rounds": range(1, match_count + 1),
        # For menu
        'league_list': League.objects.all(),
        'team_name': settings.TEAM_NAME,
    }

    return render(request, "teamstats/show_tournament.html", context)
