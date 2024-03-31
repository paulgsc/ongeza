import hashlib
import uuid
import os
from django.db import models, transaction
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone

from services.settings.upload import CHECKSUM_TYPE, EXPIRATION_DELTA, STORAGE, UPLOAD_TO, COMPLETE_EXT, INCOMPLETE_EXT


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
    ARCHIVED = 5
    STATUS_CHOICES = (
        (UPLOADING, 'Incomplete'),
        (COMPLETE, 'Complete'),
        (ABORTED, 'Aborted'),
        (ARCHIVED, 'Archived'),
    )

    upload_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,)
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
            h = hashlib.new(CHECKSUM_TYPE)
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

    @transaction.atomic
    def completed(self, completed_at=None, ext=COMPLETE_EXT):
        if completed_at is None:
            completed_at = timezone.now()

        if ext != INCOMPLETE_EXT:
            original_path = self.file.path
            self.file.name = os.path.splitext(self.file.name)[0] + ext
        self.status = self.COMPLETE
        self.completed_on = completed_at
        self.save()
        if ext != INCOMPLETE_EXT:
            os.rename(
                original_path,
                os.path.splitext(self.file.path)[0] + ext,
            )

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
        null=True,
        blank=True
    )
