

# Specify the default cache for django_ratelimit
RATELIMIT_USE_CACHE = 'default'

# Rate limit settings
RATELIMIT_KEY_FUNCTION = 'ip'  # Custom key function
RATELIMIT_RATE = '100/hour'  # Rate limit per user per hour
