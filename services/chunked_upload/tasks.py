
from chunked_upload.utils.transaction import atomic_with_abortion, abortable_task
from utils.consumer_messenger import ChannelManager
from utils.exceptions import AbortedError
from chunked_upload.utils.create_request import create_request


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
def handle_chunked_upload(*args, **kwargs):
    """
    Serialize and save a chunked upload.

    Args:
        serializer_data (dict): The data to be serialized.
        kwargs (dict): Additional keyword arguments to be passed to the serializer's save method.

    Returns:
        ChunkedUpload: The saved instance of the chunked upload.

    Raises:
        AbortedError: If the serializer data is invalid.
    """
    # import within func to avoid circular import()
    from chunked_upload.views.upload import ChunkedUploadView

    # Create a request object
    query_string = kwargs.pop('query_string', None)
    request_method = kwargs.pop('request_method', None)
    path = kwargs.pop('path', '/')
    pk = kwargs.pop('pk', None)
    request = create_request(query_string=query_string,
                             request_method=request_method, path=path, )
    print(f'request: {request} data: {request}')

    # Get the view class and instantiate it
    view = ChunkedUploadView()

    # Dispatch the request to the appropriate view method based on the request method
    if request.method == 'GET':
        response = view.handle_get(request=request, pk=pk, *args, **kwargs)
    elif request.method == 'POST':
        response = view.handle_post(request=request, pk=pk, **kwargs)
    elif request.method == 'PUT':
        response = view.handle_put(request=request, pk=pk, *args, **kwargs)
    else:
        raise AbortedError(f"Unsupported request method: {request.method}")

    # Return the response or handle it as needed
    return response


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
