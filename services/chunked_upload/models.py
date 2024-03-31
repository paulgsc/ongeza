import hashlib
import uuid

from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from celery import states
from celery.contrib.abortable import Task as AbortableTask

from ..data.models.aoi import AOI

from .settings import EXPIRATION_DELTA, UPLOAD_TO, STORAGE, DEFAULT_MODEL_USER_FIELD_NULL, DEFAULT_MODEL_USER_FIELD_BLANK


def generate_upload_id():
    return uuid.uuid4().hex


class AbstractChunkedUpload(models.Model):
    """
    Base chunked upload model. This model is abstract (doesn't create a table
    in the database).
    Inherit from this model to implement your own.
    """
    UPLOADING = 1
    COMPLETE = 2
    ABORTED = 4
    STATUS_CHOICES = (
        (UPLOADING, 'Incomplete'),
        (COMPLETE, 'Complete'),
        (ABORTED, 'Aborted'),
    )

    upload_id = models.CharField(max_length=32, unique=True, editable=False,
                                 default=generate_upload_id)
    file = models.FileField(max_length=255, upload_to=UPLOAD_TO,
                            storage=STORAGE)
    filename = models.CharField(max_length=255)
    offset = models.BigIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,
                                              default=UPLOADING)
    completed_on = models.DateTimeField(null=True, blank=True)

    @property
    def expires_on(self):
        return self.created_on + EXPIRATION_DELTA

    @property
    def expired(self):
        return self.expires_on <= timezone.now()

    @property
    def checksum(self):
        if getattr(self, '_checksum', None) is None:
            h = hashlib.new(_settings.CHECKSUM_TYPE)
            self.file.close()
            self.file.open(mode='rb')
            for chunk in self.file.chunks():
                h.update(chunk)
                self._checksum = h.hexdigest()
            self.file.close()
        return self._checksum

    def delete(self, delete_file=True, *args, **kwargs):
        if self.file:
            storage, path = self.file.storage, self.file.path
        super(AbstractChunkedUpload, self).delete(*args, **kwargs)
        if self.file and delete_file:
            storage.delete(path)

    def __str__(self):
        return u'<%s - upload_id: %s - bytes: %s - status: %s>' % (
            self.filename, self.upload_id, self.offset, self.status)

    def append_chunk(self, chunk, chunk_size=None, save=True):
        self.file.close()
        with open(self.file.path, mode='ab') as file_obj:  # mode = append+binary
            # We can use .read() safely because chunk is already in memory
            file_obj.write(chunk.read())

        if chunk_size is not None:
            self.offset += chunk_size
        elif hasattr(chunk, 'size'):
            self.offset += chunk.size
        else:
            self.offset = self.file.size
        self.checksum = None  # Clear cached md5
        if save:
            self.save()
        self.file.close()  # Flush

    def get_uploaded_file(self):
        self.file.close()
        self.file.open(mode='rb')  # mode = read+binary
        return UploadedFile(file=self.file, name=self.filename,
                            size=self.offset)

    class Meta:
        abstract = True


class ChunkedUpload(AbstractChunkedUpload):
    """
    Default chunked upload model.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chunked_uploads',
        null=DEFAULT_MODEL_USER_FIELD_NULL,
        blank=DEFAULT_MODEL_USER_FIELD_BLANK
    )


class Upload(ChunkedUpload):
    upload_dir = settings.UPLOADS_DIRECTORY
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id',
                                       for_concrete_model=False)
    is_update = models.BooleanField(default=False)
    parent_object_content_type = models.ForeignKey(
        ContentType, related_name="upload_parent",
        null=True, blank=True, on_delete=models.CASCADE
    )
    parent_object_id = models.UUIDField(null=True, blank=True)
    parent_object = GenericForeignKey('parent_object_content_type',
                                      'parent_object_id',
                                      for_concrete_model=False)
    comment = models.TextField(blank=True)
    task = models.ForeignKey(AbortableTask, related_name='upload',
                             null=True, blank=True, on_delete=models.CASCADE)

    @property
    def nstatus(self):
        if self.status == self.COMPLETE and self.task.status == states.SUCCESS:
            status = 'COMPLETED'
        elif self.status == self.COMPLETE and self.task.status == states.PENDING:
            status = 'QUEUED'
        elif self.status == self.COMPLETE and self.task.status in [states.RETRY, states.STARTED]:
            status = 'PROCESSING'
        elif self.status == self.UPLOADING:
            status = 'INCOMPLETE'
        elif self.status == self.COMPLETE and self.task.status == states.FAILURE:
            status = 'FAILED'
        elif (self.status == self.COMPLETE and self.task.status in ['ABORTED', states.REVOKED]) or self.status == self.ABORTED:
            status = 'CANCELLED'
        else:
            status = 'UNKNOWN'
        return status

    def is_aborted(self):
        return self.status == self.ABORTED

    def delete_files(self):
        if self.file:
            storage, path = self.file.storage, self.file.path
            storage.delete(path)

    def cancel(self, total_annihilation=False):
        from ..tasks import process_upload
        if self.status == self.UPLOADING:
            self.status = self.ABORTED
            self.save()
            return True
        elif self.status == self.COMPLETE and \
                states.state(self.task.status) < states.REVOKED:
            task = process_upload.AsyncResult(self.task.task_id)
            task.abort()
            self.status = self.ABORTED
            self.save()
            return True
        elif self.status >= self.ABORTED or \
                (self.task and states.state(self.task.status) >=
                 states.REVOKED):
            return False
        else:
            return None

    def get_objects_aoi_id(self):
        aoi_id = None
        if self.content_type == ContentType.objects.get_for_model(AOI):
            aoi_id = self.object_id
        else:
            try:
                aoi_id = self.content_object.aoi.id
            except AttributeError:
                pass
        if aoi_id and not AOI.objects.get(id=aoi_id).current:
            # we don't want any removed AOIs
            aoi_id = None
        return aoi_id
