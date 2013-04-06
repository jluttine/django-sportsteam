# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Player'
        db.create_table(u'teamstats_player', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
            ('firstname', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('lastname', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
        ))
        db.send_create_signal(u'teamstats', ['Player'])

        # Adding model 'League'
        db.create_table(u'teamstats_league', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=20, primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
        ))
        db.send_create_signal(u'teamstats', ['League'])

        # Adding model 'Season'
        db.create_table(u'teamstats_season', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=60, primary_key=True)),
            ('league', self.gf('django.db.models.fields.related.ForeignKey')(related_name='seasons', to=orm['teamstats.League'])),
            ('year', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'teamstats', ['Season'])

        # Adding model 'SeasonPlayer'
        db.create_table(u'teamstats_seasonplayer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamstats.Season'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamstats.Player'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('passive', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'teamstats', ['SeasonPlayer'])

        # Adding unique constraint on 'SeasonPlayer', fields ['season', 'player']
        db.create_unique(u'teamstats_seasonplayer', ['season_id', 'player_id'])

        # Adding model 'Field'
        db.create_table(u'teamstats_field', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'teamstats', ['Field'])

        # Adding model 'Match'
        db.create_table(u'teamstats_match', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('season', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamstats.Season'])),
            ('opponent', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('home', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamstats.Field'])),
            ('opponent_goals', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('opponent_owngoals', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'teamstats', ['Match'])

        # Adding model 'MatchPlayer'
        db.create_table(u'teamstats_matchplayer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamstats.Match'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamstats.SeasonPlayer'])),
            ('goals', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('assists', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'teamstats', ['MatchPlayer'])

        # Adding unique constraint on 'MatchPlayer', fields ['match', 'player']
        db.create_unique(u'teamstats_matchplayer', ['match_id', 'player_id'])

        # Adding model 'EnrolledPlayer'
        db.create_table(u'teamstats_enrolledplayer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamstats.Match'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamstats.SeasonPlayer'])),
            ('enroll', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'teamstats', ['EnrolledPlayer'])

        # Adding model 'Video'
        db.create_table(u'teamstats_video', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamstats.Match'])),
            ('mp4', self.gf('django.db.models.fields.FilePathField')(recursive=True, max_length=100, blank=True, path='/home/jluttine/workspace/django-sportsteam/sportsteam/media/videos', null=True, match='.*\\.mp4$')),
            ('ogg', self.gf('django.db.models.fields.FilePathField')(recursive=True, max_length=100, blank=True, path='/home/jluttine/workspace/django-sportsteam/sportsteam/media/videos', null=True, match='.*\\.ogv$')),
            ('webm', self.gf('django.db.models.fields.FilePathField')(recursive=True, max_length=100, blank=True, path='/home/jluttine/workspace/django-sportsteam/sportsteam/media/videos', null=True, match='.*\\.webm$')),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('part', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'teamstats', ['Video'])

        # Adding model 'SeekPoint'
        db.create_table(u'teamstats_seekpoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['teamstats.Video'])),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'teamstats', ['SeekPoint'])


    def backwards(self, orm):
        # Removing unique constraint on 'MatchPlayer', fields ['match', 'player']
        db.delete_unique(u'teamstats_matchplayer', ['match_id', 'player_id'])

        # Removing unique constraint on 'SeasonPlayer', fields ['season', 'player']
        db.delete_unique(u'teamstats_seasonplayer', ['season_id', 'player_id'])

        # Deleting model 'Player'
        db.delete_table(u'teamstats_player')

        # Deleting model 'League'
        db.delete_table(u'teamstats_league')

        # Deleting model 'Season'
        db.delete_table(u'teamstats_season')

        # Deleting model 'SeasonPlayer'
        db.delete_table(u'teamstats_seasonplayer')

        # Deleting model 'Field'
        db.delete_table(u'teamstats_field')

        # Deleting model 'Match'
        db.delete_table(u'teamstats_match')

        # Deleting model 'MatchPlayer'
        db.delete_table(u'teamstats_matchplayer')

        # Deleting model 'EnrolledPlayer'
        db.delete_table(u'teamstats_enrolledplayer')

        # Deleting model 'Video'
        db.delete_table(u'teamstats_video')

        # Deleting model 'SeekPoint'
        db.delete_table(u'teamstats_seekpoint')


    models = {
        u'teamstats.enrolledplayer': {
            'Meta': {'object_name': 'EnrolledPlayer'},
            'enroll': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamstats.Match']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamstats.SeasonPlayer']"})
        },
        u'teamstats.field': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Field'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'teamstats.league': {
            'Meta': {'ordering': "('id',)", 'object_name': 'League'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'})
        },
        u'teamstats.match': {
            'Meta': {'ordering': "('date',)", 'object_name': 'Match'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamstats.Field']"}),
            'home': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'opponent': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'opponent_goals': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'opponent_owngoals': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['teamstats.SeasonPlayer']", 'through': u"orm['teamstats.MatchPlayer']", 'symmetrical': 'False'}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamstats.Season']"})
        },
        u'teamstats.matchplayer': {
            'Meta': {'ordering': "('match__date',)", 'unique_together': "(('match', 'player'),)", 'object_name': 'MatchPlayer'},
            'assists': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'goals': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamstats.Match']"}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamstats.SeasonPlayer']"})
        },
        u'teamstats.player': {
            'Meta': {'ordering': "('lastname', 'firstname')", 'object_name': 'Player'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        },
        u'teamstats.season': {
            'Meta': {'ordering': "('-year', 'league')", 'object_name': 'Season'},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '60', 'primary_key': 'True'}),
            'league': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'seasons'", 'to': u"orm['teamstats.League']"}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['teamstats.Player']", 'through': u"orm['teamstats.SeasonPlayer']", 'symmetrical': 'False'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        u'teamstats.seasonplayer': {
            'Meta': {'ordering': "('number',)", 'unique_together': "(('season', 'player'),)", 'object_name': 'SeasonPlayer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'passive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamstats.Player']"}),
            'season': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamstats.Season']"})
        },
        u'teamstats.seekpoint': {
            'Meta': {'ordering': "('video__match__date', 'time')", 'object_name': 'SeekPoint'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamstats.Video']"})
        },
        u'teamstats.video': {
            'Meta': {'ordering': "('match__date', 'part')", 'object_name': 'Video'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'match': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['teamstats.Match']"}),
            'mp4': ('django.db.models.fields.FilePathField', [], {'recursive': 'True', 'max_length': '100', 'blank': 'True', 'path': "'/home/jluttine/workspace/django-sportsteam/sportsteam/media/videos'", 'null': 'True', 'match': "'.*\\\\.mp4$'"}),
            'ogg': ('django.db.models.fields.FilePathField', [], {'recursive': 'True', 'max_length': '100', 'blank': 'True', 'path': "'/home/jluttine/workspace/django-sportsteam/sportsteam/media/videos'", 'null': 'True', 'match': "'.*\\\\.ogv$'"}),
            'part': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'webm': ('django.db.models.fields.FilePathField', [], {'recursive': 'True', 'max_length': '100', 'blank': 'True', 'path': "'/home/jluttine/workspace/django-sportsteam/sportsteam/media/videos'", 'null': 'True', 'match': "'.*\\\\.webm$'"})
        }
    }

    complete_apps = ['teamstats']