#!/bin/bash

python manage.py makemigrations
python manage.py migrate
python manage.py create_admin_user
python manage.py create_tasks
python manage.py collectstatic --noinput

gunicorn mosamatic3.wsgi -w 2 -b 0.0.0.0:8001 -t 81240