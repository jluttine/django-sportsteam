# -*- coding: utf-8 -*-

from django.template import RequestContext, Context, loader
from django.http import HttpResponse
from django.db.models import Sum
from django.core.urlresolvers import reverse
from itertools import chain

from teamstats.models import *

def index(request):
    season_list = Season.objects.all()
    t = loader.get_template('index.html')
    c = Context({
        'season_list': season_list,
    })
    return HttpResponse(t.render(c))

## def ottelut(request, season):
##     match_list = Match.objects.filter(season__year__exact=season)
##     t = loader.get_template('ottelut.html')
##     c = Context({
##         'match_list': match_list,
##     })
##     return HttpResponse(t.render(c))

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

def kausitilasto(request, season_id):

    try:
        season = Season.objects.get(id__exact=season_id)

        # Player stats
        player_list = SeasonPlayer.objects.filter(season=season)
        table_headers = ( {'align': 'right', 'field': '#', 'sorting':'numericasc'},
                          {'align': 'left', 'field': 'Nimi', 'sorting':'stringasc'},
                          {'align': 'center', 'field': 'Ottelut', 'sorting':'numericdesc',},
                          {'align': 'center', 'field': 'Maalit', 'sorting':'numericdesc',},
                          {'align': 'center', 'field': 'Syötöt', 'sorting':'numericdesc',},
                          {'align': 'center', 'field': 'Pisteet', 'sorting':'numericdesc',}, )
        table_rows = []
        for player in player_list:
            matches = MatchPlayer.objects.filter(player=player)
            goals = matches.aggregate(goals=Sum('goals')).values()[0]
            assists = matches.aggregate(assists=Sum('assists')).values()[0]
            if goals is None:
                goals = 0
            if assists is None:
                assists = 0

            row = ( {'align': 'right', 'field': player.number, },
                    {'align': 'left', 'field': player.player, 'link': reverse('teamstats.views.pelaaja', args=[player.player.id]),},
                    {'align': 'center', 'field': matches.count(), },
                    {'align': 'center', 'field': goals, },
                    {'align': 'center', 'field': assists, },
                    {'align': 'center', 'field': goals+assists, }, )
            table_rows.append(row)

        season_list = Season.objects.all()

        # Match list
        match_list = Match.objects.filter(season=season)
        for match in match_list:
            match.goals = get_match_goals(match)
            match.result = (match.goals != None)
            if not match.result:
                # Get enrollments: 1) IN, 2) OUT, 3) Unknown
                enrolledplayers = EnrolledPlayer.objects.filter(match=match)
                match.in_players = enrolledplayers.filter(enroll=True) #.order_by('player__player__firstname')
                match.in_players = sorted(match.in_players, key=lambda player: player.player.player.shortname())
                match.out_players = enrolledplayers.filter(enroll=False) #.order_by('player__player__firstname')
                match.out_players = sorted(match.out_players, key=lambda player: player.player.player.shortname())
                unknown = list()
                for seasonplayer in SeasonPlayer.objects.filter(season=season,passive=False):
                    # TODO: In future Djangos, use .exists() !!
                    if not enrolledplayers.filter(player=seasonplayer):
                        unknown.append(seasonplayer)
                match.unknown_players = sorted(unknown, key=lambda player: player.player.shortname())

        t = loader.get_template('kausi.html')
        c = Context({
            'season': season,
            'season_list': season_list,
            'match_list': match_list,
            'table_headers': table_headers,
            'table_rows': table_rows,
            })
        return HttpResponse(t.render(c))

    except Season.DoesNotExist:
        return HttpResponse("Kautta ei olemassa.")


def pelaajat(request):
    player_list = Player.objects.all()
    table_headers = ( {'align': 'left', 'field': 'Nimi', 'sorting':'stringasc'},
                      {'align': 'center', 'field': 'Ottelut', 'sorting':'numericdesc',},
                      {'align': 'center', 'field': 'Maalit', 'sorting':'numericdesc',},
                      {'align': 'center', 'field': 'Syötöt', 'sorting':'numericdesc',},
                      {'align': 'center', 'field': 'Pisteet', 'sorting':'numericdesc',}, )
    table_rows = []
    for player in player_list:
        matches = MatchPlayer.objects.filter(player__player=player)
        goals = matches.aggregate(goals=Sum('goals')).values()[0]
        assists = matches.aggregate(assists=Sum('assists')).values()[0]
        if goals is None:
            goals = 0
        if assists is None:
            assists = 0
        row = ( {'align': 'left', 'field': player, 'link': reverse('teamstats.views.pelaaja', args=[player.id]),},
                {'align': 'center', 'field': matches.count(), },
                {'align': 'center', 'field': goals, },
                {'align': 'center', 'field': assists, },
                {'align': 'center', 'field': goals+assists, }, )
        table_rows.append(row)

    season_list = Season.objects.all()

    table_default_sort = ( {'column': 0, 'descending':0} )
    
    t = loader.get_template('pelaajat.html')
    c = Context({
        'table_headers': table_headers,
        'table_rows': table_rows,
        'table_default_sort': table_default_sort,
        'season_list': season_list,
        })
    return HttpResponse(t.render(c))

def ottelu(request, match_id):
    try:
        match = Match.objects.get(pk=match_id)

        season_list = Season.objects.all()

        video_list = Video.objects.filter(match=match)
        for video in video_list:
            video.seekpoint_list = SeekPoint.objects.filter(video=video)

        match.goals = get_match_goals(match)
        result = (match.goals != None)

        if result:
            # Print the result
            players = MatchPlayer.objects.filter(match=match)
            table_headers = ( {'align': 'right', 'field': '#', 'sorting':'numericasc', },
                              {'align': 'left', 'field': 'Nimi', 'sorting':'stringasc',},
                              {'align': 'center', 'field': 'Maalit', 'sorting':'numericdesc',},
                              {'align': 'center', 'field': '',},
                              {'align': 'center', 'field': 'Syötöt', 'sorting':'numericdesc',},
                              {'align': 'center', 'field': '',},
                              {'align': 'center', 'field': 'Pisteet', 'sorting':'numericdesc',}, )

            table_rows = []
            for player in players:
                row = ( {'align': 'right', 'field': player.player.number,},
                        {'align': 'left', 'field': player.player.player, 'link': reverse('teamstats.views.pelaaja', args=[player.player.player.id]),},
                        {'align': 'center', 'field': player.goals, },
                        {'align': 'center', 'field': '+', },
                        {'align': 'center', 'field': player.assists, },
                        {'align': 'center', 'field': '=', },
                        {'align': 'center', 'field': player.goals+player.assists, }, )
                table_rows.append(row)

            table_footers = []
            if match.opponent_owngoals:
                table_footers = ( {'align': 'right', 'field': '',},
                        {'align': 'left', 'field': 'Omat maalit',},
                        {'align': 'center', 'field': match.opponent_owngoals, },
                        {'align': 'center', 'field': '', },
                        {'align': 'center', 'field': '', },
                        {'align': 'center', 'field': '', },
                        {'align': 'center', 'field': '', }, )

            t = loader.get_template('ottelu.html')
            c = RequestContext(request,
		{
                'match': match,
                'season_list': season_list,
                'players': players,
                'table_headers': table_headers,
                'table_rows': table_rows,
                'table_footers': table_footers,
                'result': result,
                'video_list': video_list,
                })
#            c = Context({
#                'match': match,
#                'season_list': season_list,
#                'players': players,
#                'table_headers': table_headers,
#                'table_rows': table_rows,
#                'table_footers': table_footers,
#                'result': result,
#                'video_list': video_list,
#                })
        else:
            # Register posted enrollment (if one is posted)
            try:
                post_input = request.POST['choice'].split('-')
                selected_player = int(post_input[0])
                selected_choice = int(post_input[1])
                try:
                    enroller = EnrolledPlayer.objects.get(match=match,player__id=selected_player)
                    if selected_choice == 1 or selected_choice == 2:
                        enroller.enroll = (selected_choice == 1)
                        enroller.save()
                    else:
                        enroller.delete()
                except (EnrolledPlayer.DoesNotExist):
                    if selected_choice == 1 or selected_choice == 2:
                        player = SeasonPlayer.objects.get(id=selected_player)
                        enroller = EnrolledPlayer(match=match,player=player,enroll=(selected_choice==1))
                        enroller.save()
            except (KeyError):
                pass
#                selected_player = -1
#                selected_choice = 1

            # Show in/out stats
            players = SeasonPlayer.objects.filter(season=match.season,passive=False).order_by('player')
            enrollments = EnrolledPlayer.objects.filter(match=match).order_by('player__player')
            ind = 0
            for player in players:
                if ind < len(enrollments) and player.id == enrollments[ind].player.id:
                    if enrollments[ind].enroll:
                        player.choice = 1
                    else:
                        player.choice = 2
                    ind = ind + 1
                else:
                    player.choice = 3
            players = sorted(players, key=lambda player: player.choice)

            t = loader.get_template('ottelu_ilmot.html')
            c = RequestContext(request,
	        {
                'players': players,
                'match': match,
                'season_list': season_list,
                # 'result': result,
                })
#            c = Context({
#                'players': players,
#                'match': match,
#                'season_list': season_list,
#                # 'result': result,
#                })

        return HttpResponse(t.render(c))
    except Match.DoesNotExist:
        return HttpResponse("Ottelua ei olemassa.")

def pelaaja(request, player_id):
    try:
        player = Player.objects.get(pk=player_id)

        # Register enrollment (in/out/?) if one posted
        try:
            post_input = request.POST['choice'].split('-')
            selected_match = int(post_input[0])
            selected_choice = int(post_input[1])
            match = Match.objects.get(id=selected_match)
            try:
                enroller = EnrolledPlayer.objects.get(match=match,player__player=player)
                if selected_choice == 1 or selected_choice == 2:
                    enroller.enroll = (selected_choice == 1)
                    enroller.save()
                else:
                    enroller.delete()
            except (EnrolledPlayer.DoesNotExist):
                if selected_choice == 1 or selected_choice == 2:
                    seasonplayer = SeasonPlayer.objects.get(season=match.season,player=player)
                    enroller = EnrolledPlayer(match=match,player=seasonplayer,enroll=(selected_choice==1))
                    enroller.save()
        except (KeyError, Match.DoesNotExist):
            pass

        table_headers = ( {'align': 'center', 'field': 'Kausi', 'sorting':'stringasc', },
                          {'align': 'center', 'field': 'Ottelut', 'sorting':'numericdesc',},
                          {'align': 'center', 'field': 'Maalit', 'sorting':'numericdesc',},
                          {'align': 'center', 'field': 'Syötöt', 'sorting':'numericdesc',},
                          {'align': 'center', 'field': 'Pisteet', 'sorting':'numericdesc',}, )
        season_list = Season.objects.all()

        table_rows = []

        total_games = 0
        total_goals = 0
        total_assists = 0

        seasonplayer_list = []
        for season in season_list:
            try:
                seasonplayer = SeasonPlayer.objects.get(season=season,player=player)
                matchplayers = MatchPlayer.objects.filter(player=seasonplayer,match__opponent_goals__isnull=False)
                #enrolledplayers = EnrolledPlayer.objects.filter(player=seasonplayer)

                for matchplayer in matchplayers:
                    matchplayer.match.result = True
                    matchplayer.match.goals = MatchPlayer.objects.filter(match=matchplayer.match).aggregate(Sum('goals')).values()[0] + matchplayer.match.opponent_owngoals

                enrolledplayers = list()
                
                if SeasonPlayer.objects.filter(season=season,player=player,passive=False).exists():
                    matches = Match.objects.filter(season=season,opponent_goals__isnull=True)
                else:
                    matches = []

                for match in matches:
                    match.result = False
                    try:
                        enrolledplayer = EnrolledPlayer.objects.get(match=match,player=seasonplayer)
                        if enrolledplayer.enroll:
                            enrolledplayer.choice = 1
                        else:
                            enrolledplayer.choice = 2
                    except (EnrolledPlayer.DoesNotExist):
                        enrolledplayer = EnrolledPlayer(match=match,player=seasonplayer,enroll=True)
                        enrolledplayer.choice = 3
                    enrolledplayers.append(enrolledplayer)

                seasonplayer.matchplayer_list = list(chain(matchplayers, enrolledplayers))

                seasonplayer_list.append(seasonplayer)

                games = matchplayers.count()
                goals = matchplayers.aggregate(Sum('goals')).values()[0]
                assists = matchplayers.aggregate(Sum('assists')).values()[0]
                if goals is None:
                    goals = 0
                if assists is None:
                    assists = 0
                points = goals + assists

                total_games = total_games + games
                total_goals = total_goals + goals
                total_assists = total_assists + assists
                
                row = ( {'align': 'center', 'field': unicode(season), 'link': reverse('teamstats.views.kausitilasto', args=[season.id]),},
                        {'align': 'center', 'field': games, },
                        {'align': 'center', 'field': goals, },
                        {'align': 'center', 'field': assists, },
                        {'align': 'center', 'field': goals+assists, }, )
                table_rows.append(row)
                
            except SeasonPlayer.DoesNotExist:
                pass

        table_footers = ( {'align': 'center', 'field': 'Yhteensä', },
                          {'align': 'center', 'field': total_games, },
                          {'align': 'center', 'field': total_goals, },
                          {'align': 'center', 'field': total_assists, },
                          {'align': 'center', 'field': total_goals+total_assists, }, )
        
        t = loader.get_template('pelaaja.html')
        c = RequestContext(request,
	{
            'player': player,
            'table_headers': table_headers,
            'table_rows': table_rows,
            'table_footers': table_footers,
            'seasonplayer_list': seasonplayer_list,
            'season_list': season_list,
        })
#        c = Context({
#            'player': player,
#            'table_headers': table_headers,
#            'table_rows': table_rows,
#            'table_footers': table_footers,
#            'seasonplayer_list': seasonplayer_list,
#            'season_list': season_list,
#        })
        return HttpResponse(t.render(c))
    except Player.DoesNotExist:
        return HttpResponse("Pelaajaa ei olemassa.")


