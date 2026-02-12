from decouple import config

from .base import *

# Desarrollo: subdominios con localhost (ej: dulcetinta.localhost:8000)
ROOT_DOMAIN = config("ROOT_DOMAIN", default="localhost")

#DB Development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}