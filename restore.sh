#!/bin/bash

source /home/tuhlaajapojat/ENV/bin/activate

#FILENAME=$1
#TEMP=`mktemp`.json
#gunzip --stdout $FILENAME > $TEMP
python manage.py flush --no-initial-data
#python manage.py loaddata $TEMP
python manage.py loaddata $1
