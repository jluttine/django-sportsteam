# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-08-10 19:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EnrolledPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enroll', models.BooleanField()),
            ],
            options={
                'ordering': ('-enroll', 'player'),
            },
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=300, null=True)),
            ],
            options={
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opponent', models.CharField(max_length=30)),
                ('date', models.DateTimeField()),
                ('home', models.BooleanField()),
                ('opponent_goals', models.IntegerField(blank=True, null=True)),
                ('opponent_owngoals', models.IntegerField(blank=True, default=0)),
                ('comment', models.TextField(blank=True, null=True)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamstats.Field')),
            ],
            options={
                'ordering': ('date',),
            },
        ),
        migrations.CreateModel(
            name='MatchPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goals', models.IntegerField(default=0)),
                ('assists', models.IntegerField(default=0)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamstats.Match')),
            ],
            options={
                'ordering': ('match__date',),
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.CharField(max_length=60, primary_key=True, serialize=False)),
                ('firstname', models.CharField(max_length=30)),
                ('lastname', models.CharField(max_length=30)),
                ('nickname', models.CharField(blank=True, max_length=30, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
            options={
                'ordering': ('lastname', 'firstname'),
            },
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.CharField(max_length=60, primary_key=True, serialize=False)),
                ('year', models.CharField(max_length=60)),
                ('url', models.URLField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seasons', to='teamstats.League')),
            ],
            options={
                'ordering': ('-year', 'league'),
            },
        ),
        migrations.CreateModel(
            name='SeasonPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('passive', models.BooleanField()),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamstats.Player')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamstats.Season')),
            ],
            options={
                'ordering': ('number',),
            },
        ),
        migrations.CreateModel(
            name='SeekPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField()),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ('video__match__date', 'time'),
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mp4', models.FilePathField(blank=True, match='.*\\.mp4$', null=True, path='/home/jluttine/Workspace/django-sportsteam/media/videos', recursive=True)),
                ('ogg', models.FilePathField(blank=True, match='.*\\.ogv$', null=True, path='/home/jluttine/Workspace/django-sportsteam/media/videos', recursive=True)),
                ('webm', models.FilePathField(blank=True, match='.*\\.webm$', null=True, path='/home/jluttine/Workspace/django-sportsteam/media/videos', recursive=True)),
                ('title', models.CharField(max_length=30)),
                ('part', models.IntegerField()),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamstats.Match')),
            ],
            options={
                'ordering': ('match__date', 'part'),
            },
        ),
        migrations.AddField(
            model_name='seekpoint',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamstats.Video'),
        ),
        migrations.AddField(
            model_name='season',
            name='players',
            field=models.ManyToManyField(through='teamstats.SeasonPlayer', to='teamstats.Player'),
        ),
        migrations.AddField(
            model_name='matchplayer',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamstats.SeasonPlayer'),
        ),
        migrations.AddField(
            model_name='match',
            name='players',
            field=models.ManyToManyField(through='teamstats.MatchPlayer', to='teamstats.SeasonPlayer'),
        ),
        migrations.AddField(
            model_name='match',
            name='season',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamstats.Season'),
        ),
        migrations.AddField(
            model_name='enrolledplayer',
            name='match',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamstats.Match'),
        ),
        migrations.AddField(
            model_name='enrolledplayer',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teamstats.SeasonPlayer'),
        ),
        migrations.AlterUniqueTogether(
            name='seasonplayer',
            unique_together=set([('season', 'player')]),
        ),
        migrations.AlterUniqueTogether(
            name='matchplayer',
            unique_together=set([('match', 'player')]),
        ),
        migrations.AlterUniqueTogether(
            name='enrolledplayer',
            unique_together=set([('match', 'player')]),
        ),
    ]
