import os
import re

import sys
#cmd_folder = '/home/jluttine'
cmd_folder = '/home/jluttine/tuhlaajapojat'
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sportsteam.settings")
#os.environ['DJANGO_SETTINGS_MODULE'] = 'sportsteam.settings'

from teamstats.models import *

def get_addresses(list):

    print 'Trying to match a list: ' + list

    # Some aliases :)
    if list.lower() == 'vuokravaioma':
        list = 'jaakko.luttinen'

    # Try if for everyone
    if list.lower() == 'tuhlaajapojat':
        players = Player.objects.all()
        emails = [player.email for player in players if player.email]
        emails = filter(None, emails)
        return emails, '[Tuhlaajapojat] '

    # Check short aliases for most recent seasons of leagues
    # (e.g., 'hakid'->'HaKiD 2015' if 2015 is the latest season of HaKiD).
    try:
        season = Season.objects.filter(league__id__iexact=list).order_by('-year')[0]
    except IndexError:
        # Try matching to full season IDs
        try:
            season = Season.objects.get(id__iexact=list)
        except Season.DoesNotExist:
            season = None
    if season is not None:
        print('Matched season:', season)
        players = SeasonPlayer.objects.filter(season__id=season.id,passive=False)
        emails = [player.player.email for player in players]
        emails = filter(None, emails)
        return emails, '[Tuhlaajapojat-' + unicode(season.league) + '] '
    else:
        print('Did not match any season')

    # Try matching to player IDs
    try:
        player = Player.objects.get(id__iexact=list)
    except Player.DoesNotExist:
        pass
    else:
        return [player.email], ''

    print 'Did not find recipients for %s' % list 

    # No match
    return None, ''

