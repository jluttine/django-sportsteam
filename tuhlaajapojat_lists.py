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

    # Try if for everyone
    if list.lower() == 'tuhlaajapojat':
        players = Player.objects.all()
        emails = [player.email for player in players if player.email]
        emails = filter(None, emails)
        return emails, '[Tuhlaajapojat] '

    # Check team aliases
    if list.lower() == 'tuhlaajapojat-fmhd':
        list = 'tuhlaajapojat-fmhd2012'
    if list.lower() == 'tuhlaajapojat-fmhm':
        list = 'tuhlaajapojat-fmhm2013'
    if list.lower() == 'tuhlaajapojat-esport':
        list = 'tuhlaajapojat-esport2013'
    if list.lower() == 'tuhlaajapojat-haku2':
        list = 'tuhlaajapojat-haku22013'
    if list.lower() == 'tuhlaajapojat-hakud':
        list = 'tuhlaajapojat-hakud2013'
    if list.lower() == 'tuhlaajapojat-hakid':
        list = 'tuhlaajapojat-hakid2012'
    if list.lower() == 'tuhlaajapojat-hakim':
        list = 'tuhlaajapojat-hakim2013'
    if list.lower() == 'tuhlaajapojat-srksm':
        list = 'tuhlaajapojat-srksm2013'

    # Try matching to season IDs
    id = re.search('tuhlaajapojat-(?P<id>.+)', list.lower())
    if id:
        season = Season.objects.get(id__iexact=id.group('id'))
        if season:
            players = SeasonPlayer.objects.filter(season__id=season.id,passive=False)
            emails = [player.player.email for player in players]
            emails = filter(None, emails)
            return emails, '[Tuhlaajapojat-' + unicode(season.league) + '] '

    # Try matching to players
    try:
        player = Player.objects.get(id__iexact=list)
        if player.email:
            return [player.email], ''
    except:
        email = None

    print 'Did not find a match'

    # No match
    return None, ''

