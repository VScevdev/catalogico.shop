from .base import *

# Forzar HTTPS
SECURE_SSL_REDIRECT = True

# HTTPS Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Cookies Security
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    "https://dominio.com",
    "https://www.dominio.com",
]

# Header Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HSTS
# SECURE_HSTS_SECONDS = 31536000 # 1 año
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Static Root
STATIC_ROOT = BASE_DIR / "staticfiles"
