#!/bin/bash

SUFFIX=`date +%Y%m%d_%H%M%S`
FILENAME=fixtures/tuhlaajapojat_$SUFFIX.json
# Dump data to fixture
python manage.py dumpdata --format=json > $FILENAME
gzip $FILENAME
