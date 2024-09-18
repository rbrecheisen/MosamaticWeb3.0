#!/bin/bash

# pip install --upgrade -r /requirements.txt

python manage.py makemigrations
python manage.py migrate auth
python manage.py makemigrations app
python manage.py migrate
python manage.py collectstatic --noinput > /dev/null

gunicorn mosamatic.wsgi -w 2 -b 0.0.0.0:8001 -t 81240
# python manage.py runserver 8002
