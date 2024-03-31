import os
# Set Redis configurations using environment variables
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)

# Set Django Caching to use Redis
CACHE_BACKEND = "django_redis.cache.RedisCache"
CACHE_LOCATION = os.environ.get('REDIS_URL')

# Optional: Set the Redis password if provided by Railway Docker
if REDIS_PASSWORD:
    CACHE_LOCATION += f"?password={REDIS_PASSWORD}"

CACHES = {
    "default": {
        "BACKEND": CACHE_BACKEND,
        "LOCATION": CACHE_LOCATION,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
}
