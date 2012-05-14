#!/bin/sh

FILENAME=$1
TEMP=`mktemp`.json
gunzip --stdout $FILENAME > $TEMP
python manage.py flush --noinput
python manage.py loaddata $TEMP
