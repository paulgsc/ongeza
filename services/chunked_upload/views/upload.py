"""
/*
 * This code is adapted from the work originally created by Julio M Alegria in 2015,
 * and modified by Jarrett A Keifer in 2015, and is licensed under the MIT-Zero License.
 */

"""

import re

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework import status
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from services.settings.upload import CHECKSUM_TYPE, MAX_BYTES
from utils.queries import owner_or_admin
from utils.exceptions import ChunkedUploadError
from chunked_upload.serializers import ChunkedUploadSerializer, ChunkedUploadReadOnlySerializer
from ..tasks import append_chunk_task, save_chunked_upload, checksum_check
from ..models import ChunkedUpload


class ChunkedUploadBaseView(GenericAPIView):
    """
    Base view for the rest of chunked upload views.
    """

    model = ChunkedUpload
    user_field_name = 'user'
    serializer_class = ChunkedUploadSerializer
    # Define permission classes at the class level
    # permission_classes = [IsAuthenticated]

    @property
    def response_serializer_class(self):
        return self.serializer_class

    def get_queryset(self):
        """
        Get (and filter) ChunkedUpload queryset.
        By default, users can only continue uploading their own uploads.
        """
        queryset = self.model.objects.all()
        return owner_or_admin(queryset, self.request)

    def handle_post(self, request, *args, **kwargs):
        """
        Placeholder method for handling POST requests.
        """
        raise NotImplementedError

    def handle_put(self, request, *args, **kwargs):
        """
        Placeholder method for handling PUT requests.
        """
        raise NotImplementedError

    def handle_get(self, request, *args, **kwargs):
        """
        Placeholder method for handling GET requests.
        """
        raise NotImplementedError

    def filter_queryset(self, queryset):
        """
        Filter queryset based on user authentication.
        """
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            return queryset.filter(**{self.user_field_name: self.request.user})
        else:
            return queryset.none()

    def handle_error(self, error):
        """
        Handle errors by returning a response.
        """
        return Response(error.data, status=error.status_code)

    def check_permissions(self, request):
        """
        Check permissions for the request.
        """
        for permission_class in self.permission_classes:
            if not permission_class().has_permission(request, self):
                self.permission_denied(request)

    def permission_denied(self, request):
        """
        Handle permission denied.
        """
        raise PermissionDenied()

    def put(self, request, *args, pk=None, **kwargs):
        """
        Handle PUT requests.
        """
        try:
            return self.handle_put(request, pk=pk, *args, **kwargs)
        except ChunkedUploadError as error:
            return Response(error.data, status=error.status_code)

    def post(self, request, *args, pk=None, **kwargs):
        """
        Handle POST requests.
        """
        try:
            return self.handle_post(request, pk=pk, *args, **kwargs)
        except ChunkedUploadError as error:
            return Response(error.data, status=error.status_code)

    def get(self, request, *args, pk=None, **kwargs):
        """
        Handle GET requests.
        """
        try:
            return self.handle_get(request, pk=pk, *args, **kwargs)
        except ChunkedUploadError as error:
            return Response(error.data, status=error.status_code)


class ChunkedUploadView(ListModelMixin, RetrieveModelMixin,
                        ChunkedUploadBaseView):
    """
    Uploads large files in multiple chunks. Also, has the ability to resume
    if the upload is interrupted. PUT without upload ID to create an upload
    and POST to complete the upload. POST with a complete file to upload a
    whole file in one go. Method `on_completion` is a placeholder to
    define what to do when upload is complete.
    """

    # I wouldn't recommend turning off the checksum check,
    # unless it is signifcantly impacting performance.
    # Proceed at your own risk.
    do_checksum_check = True

    field_name = 'file'
    content_range_pattern = re.compile(
        r'^bytes (?P<start>\d+)-(?P<end>\d+)/(?P<total>\d+)$'
    )
    max_bytes = MAX_BYTES  # Max amount of data that can be uploaded

    def on_completion(self, upload, request):
        """
        Initiates asynchronous processing for an uploaded file and saves the upload record.

        This function is likely called after a file upload is completed successfully.
        It performs the following actions:

        1. Schedules the `process_upload` Celery task asynchronously to process the uploaded file.
        2. Creates or retrieves a `TaskMeta` object associated with the upload, linking it
        to the task ID for tracking purposes.
        3. Saves the updated `Upload` object to the database, including the task ID relationship.

        Args:
            upload (Upload object): The uploaded file object.
            request (HttpRequest): The Django request object (may or may not be used).
        """

        result = process_upload.delay(str(upload.id))
        upload.task, created = TaskMeta.objects.get_or_create(
            task_id=result.task_id)
        upload.save()

    def get_max_bytes(self, request):
        """
        Used to limit the max amount of data that can be uploaded. `None` means
        no limit.
        You can override this to have a custom `max_bytes`, e.g. based on
        logged user.
        """

        return self.max_bytes

    def is_valid_chunked_upload(self, chunked_upload):
        """
        Check if chunked upload has already expired or is already complete.
        """
        if chunked_upload.expired:
            raise ChunkedUploadError(status=status.HTTP_410_GONE,
                                     detail='Upload has expired')
        error_msg = 'Upload has already been marked as "%s"'
        if chunked_upload.status == chunked_upload.COMPLETE:
            raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
                                     detail=error_msg % 'complete')

    def _put_chunk(self, request, *args, pk=None, whole=False, **kwargs):
        try:
            chunk = request.data[self.field_name]
        except KeyError as exc:
            raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
                                     detail='No chunk file was submitted') from exc

        if whole:
            start = 0
            total = chunk.size
            end = total - 1
        else:
            content_range = request.META.get('HTTP_CONTENT_RANGE', '')
            match = self.content_range_pattern.match(content_range)
            if not match:
                raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
                                         detail='Error in request headers')

            start = int(match.group('start'))
            end = int(match.group('end'))
            total = int(match.group('total'))

        chunk_size = end - start + 1
        max_bytes = self.get_max_bytes(request)

        if end > total:
            raise ChunkedUploadError(
                status=status.HTTP_400_BAD_REQUEST,
                detail='End of chunk exceeds reported total (%s bytes)' % total
            )

        if max_bytes is not None and total > max_bytes:
            raise ChunkedUploadError(
                status=status.HTTP_400_BAD_REQUEST,
                detail='Size of file exceeds the limit (%s bytes)' % max_bytes
            )

        if chunk.size != chunk_size:
            raise ChunkedUploadError(
                status=status.HTTP_400_BAD_REQUEST,
                detail="File size doesn't match headers: file size is {} but {} reported".format(
                    chunk.size,
                    chunk_size,
                ),
            )

        try:
            if pk:
                upload_id = pk
                chunked_upload = get_object_or_404(self.get_queryset(),
                                                   pk=upload_id)
                self.is_valid_chunked_upload(chunked_upload)
                if chunked_upload.offset != start:
                    raise ChunkedUploadError(
                        status=status.HTTP_400_BAD_REQUEST,
                        detail='Offsets do not match',
                        expected_offset=chunked_upload.offset,
                        provided_offset=start,
                    )

                task = append_chunk_task.delay(
                    chunked_upload, chunk, chunk_size)
                return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)

            kwargs = {'offset': chunk.size}

            if hasattr(self.model, self.user_field_name):
                if hasattr(request, 'user') and request.user.is_authenticated:
                    kwargs[self.user_field_name] = request.user
                else:
                    raise ChunkedUploadError(
                        status=status.HTTP_400_BAD_REQUEST,
                        detail="Upload requires user authentication but user cannot be determined",
                    )
                # Create a Celery task to serialize and save the data asynchronously
                task = save_chunked_upload.delay(request.data, kwargs)
                return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            # Handle the InvalidSerializerData exception raised by the task
            raise ChunkedUploadError(
                status=status.HTTP_400_BAD_REQUEST, detail=exc.args[0]) from exc

    def _put(self, request, *args, pk=None, **kwargs):
        if pk is None:
            raise ChunkedUploadError(
                status=status.HTTP_400_BAD_REQUEST,
                detail="A primary key (pk) is required for updating an existing ChunkedUpload instance."
            )

        chunked_upload = self._put_chunk(request, pk=pk, *args, **kwargs)
        return Response(
            self.response_serializer_class(chunked_upload,
                                           context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    def checksum_check(self, chunked_upload, checksum):
        """
        Verify if checksum sent by client matches generated checksum.
        """
        if chunked_upload.checksum != checksum:
            raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
                                     detail='checksum does not match')

    def handle_post(self, request, *args, pk=None, **kwargs) -> Response:
        # If pk is provided, use it as the upload_id
        upload_id = pk

        # If pk is not provided, handle chunked upload asynchronously
        if not pk:
            self._put_chunk(request, pk=pk, *args, **kwargs)

        # Check if checksum is provided
        checksum = request.data.get(CHECKSUM_TYPE)
        if self.do_checksum_check and not checksum:
            raise ChunkedUploadError(
                status=status.HTTP_400_BAD_REQUEST,
                detail="Checksum of type '{}' is required".format(
                    CHECKSUM_TYPE),
            )

        # Get the corresponding object if chunked_upload is not None
        chunked_upload = get_object_or_404(self.get_queryset(), pk=upload_id)

        # Validate the chunked upload
        self.is_valid_chunked_upload(chunked_upload)

        # Perform checksum check if required
        serializer = ChunkedUploadReadOnlySerializer
        if self.do_checksum_check:
            if should_use_celery(chunked_upload.file.size):
                task = checksum_check.delay(
                    serializer, chunked_upload, checksum)
                return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
            else:
                self.checksum_check(chunked_upload, checksum)

        # Handle completion
        return self.on_completion(chunked_upload, request)

    @method_decorator(cache_page(0))
    def _get(self, request, *args, pk=None, **kwargs):
        if pk:
            return self.retrieve(request, pk=pk, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)
