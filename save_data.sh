#!/bin/bash

# Dump data to fixture
python manage.py dumpdata --format=json --indent=2 teamstats > initial_data.json
