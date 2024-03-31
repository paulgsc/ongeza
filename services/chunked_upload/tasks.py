
from utils.transaction import abortable_task
from utils.consumer_messenger import ChannelManager
from utils.exceptions import ChunkedUploadError
from .views.upload import ChunkedUploadView


@abortable_task
def process_upload_chunk(self, request_data, pk=None, whole=False, **kwargs):
    # Import the necessary modules and classes here

    view = ChunkedUploadView()

    try:
        chunk = request_data[view.field_name]
    except KeyError:
        raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
                                 detail='No chunk file was submitted')

    # ... (rest of the _put_chunk method logic)

    chunked_upload = view._put_chunk(
        request_data, pk=pk, whole=whole, **kwargs)
    return chunked_upload.id


@abortable_task
def pub_upload_msg_to_broker(channel_name, message):
    ChannelManager.publish_message_to_broker(
        message=message,
        channel_name=channel_name,
    )


@abortable_task
def checksum_check(chunked_upload, checksum):
    """
`   Verify if checksum sent by client matches generated checksum.
    """
    if chunked_upload.checksum != checksum:
        raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
                                 detail='checksum does not match')

    # Mark the upload as completed
    chunked_upload.completed()
