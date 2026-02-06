from decouple import config

from .base import *

# Desarrollo: subdominios con localhost (ej: dulcetinta.localhost:8000)
ROOT_DOMAIN = config("ROOT_DOMAIN", default="localhost")
