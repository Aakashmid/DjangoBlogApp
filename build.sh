#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Create superuser
# python manage.py createsuperuser --noinput --username smart --password keepgrowing

python - <<EOF
from django.contrib.auth.models import User

username = 'smart'
email = 'admin@example.com'
password = 'keepgrowing'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
else:
    print("Superuser already exists.")
EOF