# Settings for CORS - Cross-Origin Resource Sharing
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Access_control_CORS
# https://github.com/ottoyiu/django-cors-headers

from django.conf import settings

# Extend Django's default INSTALLED_APPS if needed
INSTALLED_APPS = getattr(settings, 'INSTALLED_APPS', [])

# Append additional apps
INSTALLED_APPS += [
    'corsheaders',
    # Add other apps here
]

CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
)

# we only want to allow access to the api
CORS_URLS_REGEX = r'^/api/.*$'

# we can also allow cookies, but this is a security risk
# and doesn't seem to be necessary
# CORS_ALLOW_CREDENTIALS = True
