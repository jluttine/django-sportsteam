#!/bin/bash

source /home/tuhlaajapojat/ENV/bin/activate

# Dump data to fixture
if [ "$#" == 0 ]
then
    SUFFIX=`date +%Y%m%d_%H%M%S`
    FILENAME=fixtures/tuhlaajapojat_$SUFFIX.json
    echo "Use default backup file $FILENAME"
else
    FILENAME=$1
fi

python manage.py dumpdata --indent=2 --format=json teamstats > $FILENAME
gzip $FILENAME
