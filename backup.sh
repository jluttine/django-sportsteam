#!/bin/bash

# Dump data to fixture
python manage.py dumpdata --format=json > $1
gzip $1
