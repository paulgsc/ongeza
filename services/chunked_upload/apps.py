from django.apps import AppConfig
from utils.consumer_messenger import ChannelManager


class ChunkedUploadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chunked_upload'

    def ready(self):
        # Run the ChannelManager on server start
        channel_manager = ChannelManager()
        channel_manager.main()
        import chunked_upload.signals
