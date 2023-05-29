import os

from .base import *

SECRET_KEY = os.getenv("TOTUM_SECRET", "SECRET_DEV_KEY")
DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
