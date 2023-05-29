#!/usr/bin/env sh
# start-server.sh
source /totum/.venv/bin/activate
python /totum/manage.py migrate
gunicorn Totum.wsgi:application --bind 0.0.0.0:8753 --daemon
nginx -g 'daemon off;'