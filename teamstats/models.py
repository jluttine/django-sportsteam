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

from django.db import models

from django.conf import settings
#from sportsteam import settings

class Player(models.Model):
    id = models.CharField(max_length=60, primary_key=True)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    nickname = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
 
    def shortname(self):
        if self.nickname:
            return self.nickname
        else:
            return self.firstname

    class Meta:
        ordering = ('lastname', 'firstname')

    def __unicode__(self):
        if self.nickname == "":
            return self.lastname + " " + self.firstname
        else:
            return self.lastname + " " + "\"" + self.nickname + "\"" + " " + self.firstname

class League(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=300,blank=True,null=True)

    def __unicode__(self):
        return self.id

class Season(models.Model):
    id = models.CharField(max_length=60, primary_key=True)
    league = models.ForeignKey(League)
    year = models.CharField(max_length=60)
    url = models.URLField(blank=True,null=True)
    comment = models.TextField(blank=True,null=True)
    players = models.ManyToManyField(Player, through='SeasonPlayer')

    class Meta:
        ordering = ('-year', 'league__id')

    def __unicode__(self):
        return unicode(self.league) + " " + self.year

class SeasonPlayer(models.Model):
    season = models.ForeignKey(Season)
    player = models.ForeignKey(Player)
    number = models.IntegerField()
    passive = models.BooleanField()

    class Meta:
        ordering = ('number',)

    def __unicode__(self):
        return "#" + unicode(self.number) + " " + \
               unicode(self.player) + " (" + unicode(self.season) + ")"

class Field(models.Model):
    name = models.CharField(max_length=40)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

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

    class Meta:
        ordering = ('date',)

    def __unicode__(self):
        return self.opponent + self.date.strftime(" (%a %d.%m.%Y klo %H:%M)")

class MatchPlayer(models.Model):
    match = models.ForeignKey(Match)
    player = models.ForeignKey(SeasonPlayer)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)

    class Meta:
        ordering = ('match__date',)

    def __unicode__(self):
        return unicode(self.player) + ": " + unicode(self.match)

class EnrolledPlayer(models.Model):
    match = models.ForeignKey(Match)
    player = models.ForeignKey(SeasonPlayer)
    enroll = models.BooleanField()

class Video(models.Model):
    match = models.ForeignKey(Match)
    mp4 = models.FilePathField(path=(settings.MEDIA_ROOT+'videos'),
                               match=".*\.mp4$",
                               recursive=True,
                               blank=False,
                               null=False)
    ogg = models.FilePathField(path=(settings.MEDIA_ROOT+'videos'),
                               match=".*\.ogv$",
                               recursive=True,
                               blank=False,
                               null=False)
    ## filename = models.FilePathField(path=(settings.MEDIA_ROOT+'videos'),
    ##                            recursive=True,
    ##                            blank=False,
    ##                            null=False)
    title = models.CharField(max_length=30)
    part = models.IntegerField()

    class Meta:
        ordering = ('match__date', 'part',)

    def url_mp4(self):
        path = self._meta.get_field('mp4').path
        return settings.MEDIA_URL + 'videos' + self.mp4.replace(path, '', 1)

    def url_ogg(self):
        path = self._meta.get_field('ogg').path
        return settings.MEDIA_URL + 'videos' + self.ogg.replace(path, '', 1)

    def __unicode__(self):
        return unicode(self.match) + " - " + self.title

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
        
    def __unicode__(self):
        return unicode(self.video) + " " + self.minuteseconds() + " " + unicode(self.description)

