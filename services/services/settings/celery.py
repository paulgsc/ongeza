import os
from django.conf import settings

# Extend Django's default INSTALLED_APPS if needed
INSTALLED_APPS = getattr(settings, 'INSTALLED_APPS', [])

# Append additional apps
INSTALLED_APPS += [
    'django_celery_beat',
    # Add other apps here
]


CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Los_Angeles'
CELERY_RESULT_EXPIRES = 5  # Results expire after 24 hours
CELERY_REDIRECT_STDOUTS = False

# CELERY_BEAT_SCHEDULE = {
#     'chunk_upload': {
#         'task': 'tradingbot.tasks.tasks.fetch_price_data',
#         'schedule': 300.0,  # Run every 5 seconds
#     },
# }
BROKER_CONNECTION_MAX_RETRIES = 3
