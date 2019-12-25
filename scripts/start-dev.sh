#!/bin/sh
pip install -r /app/requirements.txt
python manage.py migrate
python manage.py runserver
