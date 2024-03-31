# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ChunkedUpload
from .tasks import pub_upload_msg_to_broker


@receiver(post_save, sender=ChunkedUpload)
def handle_model_update(sender, instance, **kwargs):
    # Check if the model update is for a chunk upload
    if instance.is_chunk_upload:  # Replace this condition with your logic
        # Invoke the Celery task
        pub_upload_msg_to_broker.delay(instance.channel_name, instance.message)
