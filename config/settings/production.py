from .base import *

# Forzar HTTPS
SECURE_SSL_REDIRECT = True

# HTTPS Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Cookies Security
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# CSRF Trusted Origins (Render)
# Definir en Render como lista separada por coma, por ejemplo:
# CSRF_TRUSTED_ORIGINS="https://tu-app.onrender.com,https://www.tudominio.com"
_csrf_trusted_origins_raw = config("CSRF_TRUSTED_ORIGINS", default="")
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in _csrf_trusted_origins_raw.split(",")
    if origin.strip()
]

# Header Security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
USE_X_FORWARDED_HOST = True
X_FRAME_OPTIONS = "DENY"

# HSTS
SECURE_HSTS_SECONDS = 60 # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# Static Root
STATIC_ROOT = BASE_DIR / "staticfiles"

# Cloudinary Settings

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
}

CLOUDINARY_URL = config('CLOUDINARY_URL')