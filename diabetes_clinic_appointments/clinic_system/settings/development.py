"""
Development environment settings.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Logging configuration for development (verbose)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CSRF settings for development (less restrictive)
CSRF_COOKIE_SECURE = False  # Allow HTTP in development
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',  # Common React/Vue dev server
    'http://127.0.0.1:3000',
]

# CORS settings for development (permissive for easier frontend development)
import os
cors_enabled = os.getenv('ENABLE_CORS_IN_DEV', 'False') == 'True'

if cors_enabled:
    # Allow specific origins or all origins in development
    CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS_DEV', 'True') == 'True'

    if not CORS_ALLOW_ALL_ORIGINS:
        CORS_ALLOWED_ORIGINS = [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://localhost:3001',
            'http://127.0.0.1:3001',
            'http://localhost:8080',
            'http://127.0.0.1:8080',
        ]

    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOWED_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['*']  # Allow all headers in development
else:
    # CORS disabled by default in development (if app is monolithic)
    CORS_ALLOW_ALL_ORIGINS = False
