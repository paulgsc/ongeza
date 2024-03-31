
from chunked_upload.utils.transaction import atomic_with_abortion, abortable_task
from utils.consumer_messenger import ChannelManager
from utils.exceptions import AbortedError


@abortable_task
def pub_upload_msg_to_broker(channel_name, message):
    """
    Publish a message to a broker channel.

    Args:
        channel_name (str): The name of the broker channel.
        message (dict): The message to be published.

    Returns:
        None
    """
    ChannelManager.publish_message_to_broker(
        message=message,
        channel_name=channel_name,
    )


@abortable_task
@atomic_with_abortion
def append_chunk_task(instance, chunk, chunk_size=None, save=True):
    """
    Append a chunk to an instance and save it to the database.

    Args:
        instance (ChunkedUpload): The instance to which the chunk should be appended.
        chunk (bytes): The chunk data to be appended.
        chunk_size (int, optional): The size of the chunk. Defaults to None.
        save (bool, optional): Whether to save the instance after appending the chunk. Defaults to True.

    Returns:
        None
    """
    instance.append_chunk(chunk, chunk_size, save)


@abortable_task
@atomic_with_abortion
def save_chunked_upload(serializer_cls, serializer_data, kwargs):
    """
    Serialize and save a chunked upload.

    Args:
        serializer_cls (Serializer): The serializer class to be used for serialization.
        serializer_data (dict): The data to be serialized.
        kwargs (dict): Additional keyword arguments to be passed to the serializer's save method.

    Returns:
        ChunkedUpload: The saved instance of the chunked upload.

    Raises:
        AbortedError: If the serializer data is invalid.
    """
    chunked_upload = serializer_cls(data=serializer_data)
    if not chunked_upload.is_valid():
        # Raise a custom exception with the serializer errors
        raise AbortedError(chunked_upload.errors)

    # chunked_upload is currently a serializer
    # save returns model instance
    chunked_upload = chunked_upload.save(**kwargs)
    return chunked_upload


@abortable_task
def checksum_check(serializer, instance, checksum):
    """
`   Verify if checksum sent by client matches generated checksum.
    """
    if instance.checksum != checksum:
        channel_name = 'chunk_upload'
        message = {
            'type': 'checksum_mismatch',
            'mismatch': serializer(instance).data
        }
        ChannelManager.publish_message_to_broker(
            message=message,
            channel_name=channel_name,
        )
        instance.delete()
        return

    # Mark the upload as completed
    instance.completed()
