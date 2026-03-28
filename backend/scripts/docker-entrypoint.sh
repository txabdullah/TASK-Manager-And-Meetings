#!/bin/sh
set -e
# Only Gunicorn should run migrations. Celery/Beat share the same image; parallel migrate can corrupt Postgres.
if [ "$1" = "gunicorn" ]; then
  python manage.py migrate --noinput
fi
exec "$@"
