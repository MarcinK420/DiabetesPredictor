"""
Settings package for clinic_system project.

This package contains environment-specific settings:
- base.py: Common settings for all environments
- development.py: Development environment settings
- production.py: Production environment settings

The appropriate settings module is loaded based on the DJANGO_ENVIRONMENT
environment variable (defaults to 'development').
"""

import os

# Determine which settings to use based on environment
environment = os.getenv('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    from .production import *
elif environment == 'development':
    from .development import *
else:
    raise ValueError(f"Unknown DJANGO_ENVIRONMENT: {environment}. Must be 'development' or 'production'.")
