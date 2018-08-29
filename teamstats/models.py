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


# TODO/FIXME:
# Really interesting post about higher level query API:
# https://www.dabapps.com/blog/higher-level-query-api-django-orm/

from django.db import models
from django.db.models import (Sum, Q, Avg, Count, F, Value, Case, When,
                              ExpressionWrapper, Prefetch)
from django.db.models.functions import Coalesce
from decimal import Decimal

from django.conf import settings


class MatchQuerySet(models.query.QuerySet):


    def annotate_result(self):
        return (
            self
            .annotate(
                goals=(
                    Coalesce(Sum('matchplayer__goals'), Value(0))
                    + F('opponent_owngoals')
                ),
                # Does this weird hack work? Trying to make a boolean isnull
                # operation to tell whether the game has been played or not:
                result=Count('opponent_goals')
            )
        )


    def annotate_enrollments(self, player_list):

        enrolled_players = (
            EnrolledPlayer.objects
            .annotate_shortname()
            .order_by('-enroll', 'shortname')
        )
        match_list = (
            self.prefetch_related(
                Prefetch(
                    'enrolledplayer_set',
                    enrolled_players,
                    to_attr='ordered_enrolledplayer_set'
                ),
            )
        )

        player_list = (
            player_list
            .filter(passive=False)
            .annotate_shortname()
            .order_by('shortname')
        )
        for match in match_list:
            match.not_enrolled_players = match.exclude_enrolled_players(player_list)

        return match_list


class MatchPlayerQuerySet(models.query.QuerySet):


    def annotate_points(self):
        return self.annotate(points=F('goals') + F('assists'))


PPG_ANNOTATION = Coalesce(
    ExpressionWrapper(
        Decimal('1.0') * F('points') / F('games'),
        output_field=models.FloatField()
    ),
    Value(0.0)
)

class SeasonPlayerQuerySet(models.query.QuerySet):


    def annotate_stats(self):
        return (
            self
            .annotate(
                games=Count('matchplayer'),
                goals=Coalesce(Sum('matchplayer__goals'), Value(0)),
                assists=Coalesce(Sum('matchplayer__assists'), Value(0)),
            )
            .annotate(
                points=F('goals') + F('assists'),
            )
            .annotate(
                ppg=PPG_ANNOTATION
            )
        )


    def annotate_shortname(self):
        return self.annotate(
            shortname=Coalesce(
                Case(
                    When(player__nickname__exact='', then=None),
                    default='player__nickname'
                ),
                'player__firstname',
            )
        )


class EnrolledPlayerQuerySet(models.query.QuerySet):


    def annotate_shortname(self):
        return self.annotate(
            shortname=Coalesce(
                Case(
                    When(player__player__nickname__exact='', then=None),
                    default='player__player__nickname'
                ),
                'player__player__firstname',
            )
        )


class PlayerQuerySet(models.query.QuerySet):

    def annotate_stats(self):
        return(
            self
            .annotate(
                games=Count('seasonplayer__matchplayer'),
                goals=Coalesce(Sum('seasonplayer__matchplayer__goals'), Value(0)),
                assists=Coalesce(Sum('seasonplayer__matchplayer__assists'), Value(0)),
            )
            .annotate(
                points=F('goals') + F('assists'),
            )
            .annotate(
                ppg=PPG_ANNOTATION
            )
        )


class Comparable():


    def __cmp__(self, other):
        def cmp_tuple(field):
            if field.startswith('-'):
                return getattr(other, field[1:]), getattr(self, field[1:])
            else:
                return getattr(self, field), getattr(other, field)

        # build up a list of two-tuples of values from both models, based on
        # the Meta.ordering
        comparables = map(cmp_tuple, self._meta.ordering)
        # flatten the list of two-tuples into two lists and pass that to cmp
        (x, y) = zip(*comparables)
        return (
            0  if x == y else
            -1 if x < y else
            1
        )


    def __lt__(self, b):
        return self.__cmp__(b) < 0


    def __le__(self, b):
        return self.__cmp__(b) <= 0


    def __eq__(self, b):
        return self.__cmp__(b) == 0


    def __ne__(self, b):
        return self.__cmp__(b) != 0


    def __ge__(self, b):
        return self.__cmp__(b) >= 0


    def __gt__(self, b):
        return self.__cmp__(b) > 0


class Player(models.Model):
    id = models.CharField(max_length=60, primary_key=True)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    nickname = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    objects = PlayerQuerySet.as_manager()

    # def shortname(self):
    #     if self.nickname:
    #         return self.nickname
    #     else:
    #         return self.firstname

    class Meta:
        ordering = ('lastname', 'firstname')


    def get_seasons(self, active_player=True):
        seasons = Season.objects.filter(seasonplayer__player=self)
        if active_player:
            seasons = seasons.filter(seasonplayer__passive=False)
        return seasons


    def get_matches(self):
        played_match = Q(matchplayer__player__player=self)
        might_enroll = Q(
            opponent_goals__isnull=True,
            season__in=self.get_seasons(active_player=True)
        )
        return (
            Match.objects
            .annotate(
                player_goals=Sum(Case(
                    When(matchplayer__player__player=self, then='matchplayer__goals')
                )),
                player_assists=Sum(Case(
                    When(matchplayer__player__player=self, then='matchplayer__assists')
                )),
                player_enrolled=Sum(Case(
                    When(enrolledplayer__player__player=self, then='enrolledplayer__enroll')
                ))
            )
            .filter(played_match | might_enroll)
        )


    def __str__(self):
        if not self.nickname:
            return self.lastname + " " + self.firstname
        else:
            return self.lastname + " " + "\"" + self.nickname + "\"" + " " + self.firstname


class League(models.Model, Comparable):
    id = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=300,blank=True,null=True)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.id


class Season(models.Model, Comparable):
    id = models.CharField(max_length=60, primary_key=True)
    league = models.ForeignKey(League,
                               related_name='seasons')
    year = models.CharField(max_length=60)
    url = models.URLField(blank=True,null=True)
    comment = models.TextField(blank=True,null=True)
    players = models.ManyToManyField(Player, through='SeasonPlayer')

    class Meta:
        ordering = ('-year', 'league')

    def __str__(self):
        return str(self.league) + " " + str(self.year)


class SeasonPlayer(models.Model):
    season = models.ForeignKey(Season)
    player = models.ForeignKey(Player)
    number = models.IntegerField()
    passive = models.BooleanField()

    objects = SeasonPlayerQuerySet.as_manager()

    class Meta:
        ordering = ('number',)
        unique_together = (("season", "player",),)

    def __str__(self):
        return "#" + str(self.number) + " " + \
               str(self.player) + " (" + str(self.season) + ")"


class Field(models.Model):
    name = models.CharField(max_length=40)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return str(self.name)


class Match(models.Model):
    season = models.ForeignKey(Season)
    players = models.ManyToManyField(SeasonPlayer, \
                                     through='MatchPlayer')
    opponent = models.CharField(max_length=30)
    date = models.DateTimeField()
    home = models.BooleanField()
    field = models.ForeignKey(Field)
    opponent_goals = models.IntegerField(blank=True,null=True)
    opponent_owngoals = models.IntegerField(blank=True,default=0)
    comment = models.TextField(blank=True,null=True)

    objects = MatchQuerySet.as_manager()

    class Meta:
        ordering = ('date',)

    def __str__(self):
        return str(self.opponent) + self.date.strftime(" (%a %d.%m.%Y klo %H:%M)")


    def exclude_enrolled_players(self, player_list):
        enrolled_players = [
            enrolled_player.player
            for enrolled_player in self.ordered_enrolledplayer_set
            #for enrolled_player in self.enrolledplayer_set.all()
        ]
        return [
            player
            for player in player_list
            if player not in enrolled_players
        ]


class MatchPlayer(models.Model):
    match = models.ForeignKey(Match)
    player = models.ForeignKey(SeasonPlayer)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)

    objects = MatchPlayerQuerySet.as_manager()

    class Meta:
        ordering = ('match__date',)
        unique_together = (("match", "player",),)

    def __str__(self):
        return str(self.player) + ": " + str(self.match)


class EnrolledPlayer(models.Model):
    match = models.ForeignKey(Match)
    player = models.ForeignKey(SeasonPlayer)
    enroll = models.BooleanField()

    objects = EnrolledPlayerQuerySet.as_manager()


    class Meta:
        ordering = ('-enroll', 'player')
        unique_together = (('match', 'player'))


class Video(models.Model):
    match = models.ForeignKey(Match)
    mp4 = models.FilePathField(path=(settings.MEDIA_ROOT+'videos'),
                               match=".*\.mp4$",
                               recursive=True,
                               blank=True,
                               null=True)
    ogg = models.FilePathField(path=(settings.MEDIA_ROOT+'videos'),
                               match=".*\.ogv$",
                               recursive=True,
                               blank=True,
                               null=True)
    webm = models.FilePathField(path=(settings.MEDIA_ROOT+'videos'),
                                match=".*\.webm$",
                                recursive=True,
                                blank=True,
                                null=True)
    title = models.CharField(max_length=30)
    part = models.IntegerField()

    class Meta:
        ordering = ('match__date', 'part',)

    def url_mp4(self):
        path = self._meta.get_field('mp4').path
        if self.mp4:
            filename = self.mp4.replace(path, '', 1)
        else:
            filename = ''
        return settings.MEDIA_URL + 'videos/' + filename

    def url_ogg(self):
        path = self._meta.get_field('ogg').path
        if self.ogg:
            filename = self.ogg.replace(path, '', 1)
        else:
            filename = ''
        return settings.MEDIA_URL + 'videos/' + filename

    def url_webm(self):
        path = self._meta.get_field('webm').path
        if self.webm:
            filename = self.webm.replace(path, '', 1)
        else:
            filename = ''
        return settings.MEDIA_URL + 'videos/' + filename

    def __str__(self):
        return str(self.match) + " - " + self.title

class SeekPoint(models.Model):
    video = models.ForeignKey(Video)
    time = models.TimeField()
    description = models.CharField(max_length=100)

    def seconds(self):
        return 3600*self.time.hour + 60*self.time.minute + self.time.second

    def minuteseconds(self):
        return self.time.strftime('%M:%S')

    class Meta:
        ordering = ('video__match__date', 'time',)

    def __str__(self):
        return str(self.video) + " " + self.minuteseconds() + " " + str(self.description)


class Tournament(models.Model):
    name = models.CharField(max_length=20, unique=True)
    players = models.ManyToManyField(Player, through='TournamentPlayer')

    def __str__(self):
        return str(self.name)


class TournamentPlayer(models.Model):
    tournament = models.ForeignKey(Tournament)
    player = models.ForeignKey(Player)

    class Meta:
        unique_together = (("tournament", "player",),)

    def __str__(self):
        return str(self.player) + " @ " + str(self.tournament)


class TournamentPlayerPoints(models.Model):
    tournamentplayer = models.ForeignKey(TournamentPlayer)
    points = models.IntegerField()

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return str(self.points)
