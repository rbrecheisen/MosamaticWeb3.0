#!/bin/bash

python manage.py makemigrations
python manage.py migrate

gunicorn mosamatic3.wsgi -w 2 -b 0.0.0.0:8001 -t 81240