from pathlib import Path
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Debug
DEBUG = False

# Allowed hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
    # Assuming SITE_DOMAIN_NAME is defined elsewhere
    SITE_DOMAIN_NAME,
]

# Application definition
INSTALLED_APPS = [
    # django lib
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # project apps
    'common',
    'users',
    'pets',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ebagis.urls'
WSGI_APPLICATION = 'ebagis.wsgi.application'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'US/Pacific'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Django user model
AUTH_USER_MODEL = 'auth.User'

# URL PATH SETTINGS
REST_ROOT = "api/rest/"

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / "media"
SITE_STATIC_ROOT = BASE_DIR / 'local_static'
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Message settings
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info alert-autoclose',
    messages.INFO: 'alert-info alert-dismissible',
    messages.SUCCESS: 'alert-success alert-autoclose',
    messages.WARNING: 'alert-warning alert-dismissible',
    messages.ERROR: 'alert-danger alert-dismissible',
}

MIGRATION_MODULES = {
    'sites': 'ebagis.fixtures.sites_migrations',
    'socialaccount': 'ebagis.fixtures.socialaccount_migrations',
}

# django sites
SITE_ID = 1

# project-wide email settings
EMAIL_SUBJECT_PREFIX = "[ebagis] "
DEFAULT_FROM_EMAIL = "ebagis@pdx.edu"
