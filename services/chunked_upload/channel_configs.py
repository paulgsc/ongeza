
# Channel configs for redis pubsub messenger
CHANNEL_CONFIGS = [
    {
        'call_type': 'type1',
        'celery_channels': 'channel1',
        'event': 'event1',
        'group_name': 'group1'
    },
    {
        'call_type': 'type2',
        'celery_channels': 'channel2',
        'event': 'event2',
        'group_name': 'group2'
    }
]
