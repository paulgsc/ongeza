import os

INSTALLED_APPS += (
    'django_celery_beat',
)

CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Los_Angeles'
CELERY_RESULT_EXPIRES = 5  # Results expire after 24 hours
CELERY_REDIRECT_STDOUTS = False
# Update this with your broker URL
# CELERY_BEAT_SCHEDULE = {
#     'schedule-tasks': {
#         'task': 'app.tasks.tasks.schedule_tasks',
#         'schedule': crontab(minute='*'),  # Run every minute
#     },
# }

BROKER_CONNECTION_MAX_RETRIES = 3
