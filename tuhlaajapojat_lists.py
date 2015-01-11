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

    # Check team aliases
    if list.lower() == 'adidas':
        list = 'adidas2014'
    if list.lower() == 'fmhd':
        list = 'fmhd2012'
    if list.lower() == 'fmhm':
        list = 'fmhm2014'
    if list.lower() == 'esport':
        list = 'esport2014'
    if list.lower() == 'haku2':
        list = 'haku22013'
    if list.lower() == 'hakud':
        list = 'hakud2014'
    if list.lower() == 'hakid':
        list = 'hakid2014'
    if list.lower() == 'hakim':
        list = 'hakim2013'
    if list.lower() == 'srksm':
        list = 'srksm2014'

    # Try matching to season IDs
    try:
        season = Season.objects.get(id__iexact=list)
    except Season.DoesNotExist:
        pass
    else:
        players = SeasonPlayer.objects.filter(season__id=season.id,passive=False)
        emails = [player.player.email for player in players]
        emails = filter(None, emails)
        return emails, '[Tuhlaajapojat-' + unicode(season.league) + '] '

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

