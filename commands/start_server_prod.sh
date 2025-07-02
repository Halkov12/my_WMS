#!/bin/sh

python manage.py migrate
python manage.py check
python manage.py collectstatic --noinput

python manage.py runserver 0:8010