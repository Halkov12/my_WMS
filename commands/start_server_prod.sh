#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py check
python manage.py collectstatic --noinput

gunicorn config.wsgi:application --bind 0.0.0.0:8010 --workers=3 --timeout=120