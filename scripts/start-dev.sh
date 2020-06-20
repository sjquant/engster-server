#!/bin/sh
poetry install
python manage.py migrate
python manage.py runserver
