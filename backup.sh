#!/bin/bash

SUFFIX=`date +%Y%m%d_%H%M%S`
FILENAME=$HOME/tuhlaajapojat/fixtures/tuhlaajapojat_$SUFFIX.json
MANAGE=$HOME/tuhlaajapojat/manage.py
PYTHON=/usr/bin/python
# Dump data to fixture
$PYTHON $MANAGE dumpdata --format=json > $FILENAME
gzip $FILENAME
