"""
Django settings for services project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# Generate with ./manage.py generate_encryption_key
FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Base settings file path
BASE_DIR = Path(__file__).resolve().parent.parent


# Load additional settings files
settings_files = [
    'base.py',
    'auth.py',
    'caching.py',
    'celery.py',
    'database.py',
    'logging.py',
    'rest.py',
]
