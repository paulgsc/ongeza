import os

from pathlib import Path

from split_settings.tools import optional, include

# Load configuration settings from a dedicated configuration module
from .config import load_conf_file

# Base settings file path
BASE_DIR = Path(__file__).resolve().parent.parent

# Load configuration settings
conf_settings = load_conf_file()

# Environment-specific settings
ENV = conf_settings.get('ENV', 'production')

# Basic settings
SECRET_KEY = conf_settings.get('SECRET_KEY')
DEBUG = conf_settings.get('DEBUG', False)
SITE_DOMAIN_NAME = conf_settings.get('SITE_DOMAIN_NAME')

# Celery settings
CELERY_BROKER_USER = conf_settings.get('CELERY_BROKER_USER')
CELERY_BROKER_PASSWORD = conf_settings.get('CELERY_BROKER_PASSWORD')

# Database settings
DATABASE_NAME = conf_settings.get('DATABASE_NAME')
DATABASE_USER = conf_settings.get('DATABASE_USER')
DATABASE_PASSWORD = conf_settings.get('DATABASE_PASSWORD')
DATABASE_HOST = conf_settings.get('DATABASE_HOST')
DATABASE_PORT = conf_settings.get('DATABASE_PORT')

# Load additional settings files
settings_files = [
    'base.py',
    # ... other settings files
]

# Add environment-specific settings
settings_files.append(f"{ENV}.py")  # Use f-strings for readability

# Add additional settings from configuration
settings_files.extend(conf_settings.get('ADDITIONAL_SETTING_FILES', []))

# Always include local_settings.py if present
settings_files.append(optional('local_settings.py'))

# Load all settings files
include(*settings_files, scope=globals())
