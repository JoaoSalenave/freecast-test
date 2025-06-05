#!/bin/sh

set -e

cd /app/media

echo "==> Applying migrations…"
python manage.py migrate --noinput

export DJANGO_SETTINGS_MODULE=backend.settings

if [ "$1" = "python" ]; then

  if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && \
     [ -n "$DJANGO_SUPERUSER_EMAIL" ] && \
     [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then

    echo "==> Checking for existing superuser '$DJANGO_SUPERUSER_USERNAME'…"
    export DJANGO_SETTINGS_MODULE=backend.settings

    python - <<END_SCRIPT
import os
import django

django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ["DJANGO_SUPERUSER_USERNAME"]

if not User.objects.filter(username=username).exists():
    print("====> Creating superuser '$DJANGO_SUPERUSER_USERNAME'")
    User.objects.create_superuser(
        username=username,
        email=os.environ["DJANGO_SUPERUSER_EMAIL"],
        password=os.environ["DJANGO_SUPERUSER_PASSWORD"]
    )
else:
    print("====> Superuser '$DJANGO_SUPERUSER_USERNAME' already exists, skipping.")
END_SCRIPT

  else
    echo "==> DJANGO_SUPERUSER_* not fully set; skipping superuser creation."
  fi

else
  echo "==> Not running as 'python'; skipping superuser creation in Celery container."
fi

exec "$@"