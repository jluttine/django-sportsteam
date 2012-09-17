#!/bin/sh

python manage.py flush
python manage.py loaddata data.json
