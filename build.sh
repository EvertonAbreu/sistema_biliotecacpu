#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Cria superusuário se não existir
python manage.py createsuperuser \
  --noinput \
  --username $DJANGO_SUPERUSER_USERNAME \
  --email $DJANGO_SUPERUSER_EMAIL || true