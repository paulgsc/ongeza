"""
This module provides classes for managing communication between Redis and WebSocket channels.

It includes a `ChannelManager` class for handling Redis Pub/Sub operations and updating WebSocket channels,
and a `ChannelsUpdater` utility class for sending messages to WebSocket groups.

Example usage:
Define your channel configurations:
channel_configs = [
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

Create an instance of ChannelManager with the channel configurations:
channel_manager = ChannelManager(channel_configs)

Now you can call the main method to start listening to Redis channels:
channel_manager.main()
"""

import json
import time
import redis
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .exceptions import RedisPubSubError

# TO DO: Test the singleton pattern across multiple apps.py calls


class ChannelsUpdater:
    """
    Utility class to update WebSocket channels.
    """

    @staticmethod
    def update_ws(group_name, msg):
        """
        Sends a message to a specific WebSocket group.

        Parameters:
        - group_name (str): The name of the WebSocket group.
        - msg (dict): The message to send.
        """
        # send to channel
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, msg)


class ChannelManager:
    """
    Manages communication between Redis and WebSocket channels.
    """

    _instance = None
    _redis_client = None  # Initialize a class attribute for Redis client

    def __new__(cls, channel_configs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.channel_configs = channel_configs
            cls._instance.redis_client = cls._instance.get_redis_connection()
        return cls._instance

    @classmethod
    def _get_redis_connection(cls):
        """
        Establishes a connection to Redis.

        Returns:
        - redis.Redis: The Redis client instance.
        """
        if not cls._redis_client:
            try:
                redis_instance = redis.Redis(host='localhost', port=6379, db=0)
                redis_instance.ping()
                cls._redis_client = redis_instance
            except Exception as e:
                time.sleep(5)
                raise RedisPubSubError(
                    "Failed to establish Redis connection") from e
        return cls._redis_client

    def get_redis_connection(self):
        """
        Returns the existing Redis client instance (singleton pattern).
        """
        if not self._redis_client:
            self._get_redis_connection()  # Call connection logic if not already set
        return self._redis_client

    def __init__(self, channel_configs):
        """
        Initializes the ChannelManager.

        Parameters:
        - channel_configs (list of dict): List of dictionaries containing configuration for each channel.
          Each dictionary should contain the following keys:
            - 'call_type': The type of call.
            - 'celery_channels': The channel to communicate with Celery.
            - 'event': The event type.
            - 'group_name': The name of the WebSocket group.
        """
        self.channel_configs = channel_configs

    @classmethod
    def publish_message_to_broker(cls, message, channel_name):
        """
        Publishes a message to the Redis channel.

        Parameters:
        - message (dict): The message to publish.
        """
        try:
            redis_client = cls._get_redis_connection()
            redis_client.publish(
                channel=channel_name, message=json.dumps(message))
        except Exception as e:
            raise RedisPubSubError(
                "Failed to publish message to Redis channel") from e

    def extract_msg(self, item):
        """
        Extracts a message from a Redis item.

        Parameters:
        - item (dict): The Redis item.

        Returns:
        - dict: The extracted message.
        """
        if item.get('type') is None or item.get('type') != 'pmessage':
            return None

        try:
            item_data = json.loads(
                item['data'].decode('utf8').replace("'", '"'))
        except json.decoder.JSONDecodeError as e:
            print(f'This failed: {str(e)}')
            return None

        extracted_messages = []
        for config in self.channel_configs:
            try:
                if item_data['type'] == config['call_type']:
                    data = item_data[config['event']]
                else:
                    raise RedisPubSubError(
                        "Failed to find type for channel layer")
                msg = {"type": config['call_type'], "data": data}
                extracted_messages.append((config['group_name'], msg))
            except Exception as e:
                raise RedisPubSubError(
                    "Failed to extract message from Redis item") from e

        return extracted_messages

    def main(self):
        """
        Runs the Redis listener and sends updates to WebSocket channels.
        """
        print('Start')

        pubsub = self._instance.redis_client.pubsub()
        for config in self.channel_configs:
            try:
                pubsub.psubscribe(config['celery_channels'])
            except Exception as e:
                raise RedisPubSubError(
                    "Failed to subscribe to Redis channels") from e

        for item in pubsub.listen():
            try:
                msgs = self.extract_msg(item)
                if not msgs:
                    continue
                for group_name, msg in msgs:
                    ChannelsUpdater.update_ws(group_name=group_name, msg=msg)
            except Exception as e:
                print(f"Error occurred: {str(e)}")
                # Handle or log the error as needed
