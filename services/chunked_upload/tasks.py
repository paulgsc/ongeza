from .models import Upload
from utils.transaction import abortable_task
from utils.consumer_messenger import ChannelManager
from utils.exceptions import ChunkedUploadError


@abortable_task
def process_upload_chunk(self, request_data, pk=None, whole=False, **kwargs):
    # Import the necessary modules and classes here
    from your_app.views import ChunkedUploadView

    view = ChunkedUploadView()

    try:
        chunk = request_data[view.field_name]
    except KeyError:
        raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
                                 detail='No chunk file was submitted')

    # ... (rest of the _put_chunk method logic)

    chunked_upload = view._put_chunk(request_data, pk=pk, whole=whole, **kwargs)
    return chunked_upload.id

@abortable_task
def process_upload(self, upload_id):
    # I was hoping the upload_id arg could go away,
    # and we could do upload = self.upload.get()
    # however, self is a Task, not TaskMeta, and does not have relations
    upload = Upload.objects.get(pk=upload_id)
    upload_class = ContentType.model_class(upload.content_type)
    zip_path = upload.file.path

    temp_prefix = upload_class.__name__ + "_"

    with tempdirectory(prefix=temp_prefix, dir=EBAGIS_TEMP_DIRECTORY,
                       do_not_remove=settings.DEBUG) as tempdir:
        print "Extracting upload zip to {}.".format(tempdir)
        unzipfile(zip_path, tempdir)

        temp_path = get_path_from_tempdir(tempdir)

        print "Upload to import is {}.".format(temp_path)

        self.if_aborted()

        if upload.is_update:
            imported_obj = upload_class.update(upload, temp_path)
        elif not upload.is_update:
            imported_obj = upload_class.create_from_upload(
                upload, temp_path
            )
        else:
            raise Exception("Unexpected fatal error: " +
                            "is_update not set on upload")
    return "{},{}".format(imported_obj.id, upload.content_type)

@abortable_task
def pub_upload_msg_to_broker(channel_name, message):
    ChannelManager.publish_message_to_broker(
        message= message,
        channel_name=channel_name,
        )