#!/bin/bash

# Dump data to fixture
if [ "$#" == 0 ]
then
    SUFFIX=`date +%Y%m%d_%H%M%S`
    FILENAME=fixtures/tuhlaajapojat_$SUFFIX.json
    echo "Use default backup file $FILENAME"
else
    FILENAME=$1
fi

python manage.py dumpdata --format=json > $FILENAME
gzip $FILENAME
