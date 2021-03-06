# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-01 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamstats', '0007_auto_20180901_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentmatch',
            name='away_team',
            field=models.ManyToManyField(blank=True, related_name='away_match', to='teamstats.TournamentPlayer'),
        ),
        migrations.AlterField(
            model_name='tournamentmatch',
            name='home_team',
            field=models.ManyToManyField(blank=True, related_name='home_match', to='teamstats.TournamentPlayer'),
        ),
    ]
