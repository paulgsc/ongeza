
# Channel configs for redis pubsub messenger
CHANNEL_CONFIGS = [
    {
        'call_type': 'type1',
        'celery_channels': 'chunk_upload',
        'event': 'chunk',
        'group_name': 'upload_status'
    },
]
