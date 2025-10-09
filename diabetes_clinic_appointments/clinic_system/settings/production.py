"""
Production environment settings.
"""

import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# ALLOWED_HOSTS must be set via environment variable
allowed_hosts_str = os.getenv('ALLOWED_HOSTS', '')
if not allowed_hosts_str:
    raise ValueError("ALLOWED_HOSTS environment variable must be set in production!")
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]

# Database
# Support both SQLite (for simple deployments) and PostgreSQL (recommended)
database_url = os.getenv('DATABASE_URL', '')

if database_url:
    # Use DATABASE_URL if provided (e.g., for PostgreSQL)
    # Format: postgresql://user:password@host:port/dbname
    try:
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(
                default=database_url,
                conn_max_age=600,
                conn_health_checks=True,
            )
        }
    except ImportError:
        raise ImportError(
            "dj-database-url is required when using DATABASE_URL. "
            "Install it with: pip install dj-database-url"
        )
else:
    # Fallback to SQLite if no DATABASE_URL is provided
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Security settings for production
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CSRF settings
# CSRF_TRUSTED_ORIGINS is required for HTTPS when using POST requests from allowed origins
csrf_trusted_origins_str = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_trusted_origins_str:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_trusted_origins_str.split(',') if origin.strip()]
else:
    # If not set, construct from ALLOWED_HOSTS
    CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS if not host.startswith('127.0.0.1') and not host.startswith('localhost')]

CSRF_COOKIE_HTTPONLY = os.getenv('CSRF_COOKIE_HTTPONLY', 'False') == 'True'  # False by default for JavaScript access
CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'Lax')  # Lax or Strict
CSRF_COOKIE_AGE = int(os.getenv('CSRF_COOKIE_AGE', '31449600'))  # 1 year (in seconds)

# HSTS settings (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Proxy/Load Balancer settings
# If behind nginx/Apache reverse proxy, trust X-Forwarded-Proto header
if os.getenv('TRUST_PROXY_HEADERS', 'False') == 'True':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True

# Referrer Policy - controls how much referrer information is sent
SECURE_REFERRER_POLICY = os.getenv('SECURE_REFERRER_POLICY', 'same-origin')

# Cross-Origin Opener Policy - protects against cross-origin attacks
SECURE_CROSS_ORIGIN_OPENER_POLICY = os.getenv('SECURE_CROSS_ORIGIN_OPENER_POLICY', 'same-origin')

# CORS settings
# Enable CORS only if CORS_ALLOWED_ORIGINS is set
cors_allowed_origins_str = os.getenv('CORS_ALLOWED_ORIGINS', '')
if cors_allowed_origins_str:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_allowed_origins_str.split(',') if origin.strip()]
    CORS_ALLOW_CREDENTIALS = os.getenv('CORS_ALLOW_CREDENTIALS', 'True') == 'True'

    # Allowed methods
    cors_allowed_methods_str = os.getenv('CORS_ALLOWED_METHODS', 'GET,POST,PUT,PATCH,DELETE,OPTIONS')
    CORS_ALLOWED_METHODS = [method.strip() for method in cors_allowed_methods_str.split(',')]

    # Allowed headers
    cors_allowed_headers_str = os.getenv('CORS_ALLOWED_HEADERS', '')
    if cors_allowed_headers_str:
        CORS_ALLOWED_HEADERS = [header.strip() for header in cors_allowed_headers_str.split(',')]
    else:
        # Use default headers from django-cors-headers
        from corsheaders.defaults import default_headers
        CORS_ALLOWED_HEADERS = list(default_headers)

    # Expose headers (headers that browser can access)
    cors_expose_headers_str = os.getenv('CORS_EXPOSE_HEADERS', '')
    if cors_expose_headers_str:
        CORS_EXPOSE_HEADERS = [header.strip() for header in cors_expose_headers_str.split(',')]

    CORS_ALLOW_ALL_ORIGINS = False
else:
    # CORS disabled by default in production
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = []

# Ensure logs directory exists
logs_dir = BASE_DIR / 'logs'
logs_dir.mkdir(exist_ok=True)

# Logging configuration for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Email backend for production (configure SMTP in environment variables)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
