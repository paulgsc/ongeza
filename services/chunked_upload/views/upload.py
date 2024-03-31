# import re

# from rest_framework.generics import GenericAPIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
# from rest_framework import status
# from django.core.exceptions import PermissionDenied
# from django.shortcuts import get_object_or_404
# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import cache_page
# from utils.queries import owner_or_admin
# from chunked_upload.serializers import ChunkedUploadSerializer
# from ..models import ChunkedUpload
# from ..exceptions import ChunkedUploadError


# class ChunkedUploadBaseView(GenericAPIView):
#     """
#     Base view for the rest of chunked upload views.
#     """

#     model = ChunkedUpload
#     user_field_name = 'user'
#     serializer_class = ChunkedUploadSerializer
#     # Define permission classes at the class level
#     permission_classes = [IsAuthenticated]

#     @property
#     def response_serializer_class(self):
#         return self.serializer_class

#     def get_queryset(self):
#         """
#         Get (and filter) ChunkedUpload queryset.
#         By default, users can only continue uploading their own uploads.
#         """
#         queryset = self.model.objects.all()
#         return owner_or_admin(queryset, self.request)

#     def handle_post(self, request, *args, **kwargs):
#         """
#         Placeholder method for handling POST requests.
#         """
#         raise NotImplementedError

#     def handle_put(self, request, *args, **kwargs):
#         """
#         Placeholder method for handling PUT requests.
#         """
#         raise NotImplementedError

#     def handle_get(self, request, *args, **kwargs):
#         """
#         Placeholder method for handling GET requests.
#         """
#         raise NotImplementedError

#     def filter_queryset(self, queryset):
#         """
#         Filter queryset based on user authentication.
#         """
#         if hasattr(self.request, 'user') and self.request.user.is_authenticated:
#             return queryset.filter(**{self.user_field_name: self.request.user})
#         else:
#             return queryset.none()

#     def handle_error(self, error):
#         """
#         Handle errors by returning a response.
#         """
#         return Response(error.data, status=error.status_code)

#     def check_permissions(self, request):
#         """
#         Check permissions for the request.
#         """
#         for permission_class in self.permission_classes:
#             if not permission_class().has_permission(request, self):
#                 self.permission_denied(request)

#     def permission_denied(self, request):
#         """
#         Handle permission denied.
#         """
#         raise PermissionDenied()

#     def put(self, request, pk=None, *args, **kwargs):
#         """
#         Handle PUT requests.
#         """
#         try:
#             return self.handle_put(request, pk=pk, *args, **kwargs)
#         except ChunkedUploadError as error:
#             return Response(error.data, status=error.status_code)

#     def post(self, request, pk=None, *args, **kwargs):
#         """
#         Handle POST requests.
#         """
#         try:
#             return self.handle_post(request, pk=pk, *args, **kwargs)
#         except ChunkedUploadError as error:
#             return Response(error.data, status=error.status_code)

#     def get(self, request, pk=None, *args, **kwargs):
#         """
#         Handle GET requests.
#         """
#         try:
#             return self.handle_get(request, pk=pk, *args, **kwargs)
#         except ChunkedUploadError as error:
#             return Response(error.data, status=error.status_code)


# class ChunkedUploadView(ListModelMixin, RetrieveModelMixin,
#                         ChunkedUploadBaseView):
#     """
#     Uploads large files in multiple chunks. Also, has the ability to resume
#     if the upload is interrupted. PUT without upload ID to create an upload
#     and POST to complete the upload. POST with a complete file to upload a
#     whole file in one go. Method `on_completion` is a placeholder to
#     define what to do when upload is complete.
#     """

#     # I wouldn't recommend turning off the checksum check,
#     # unless it is signifcantly impacting performance.
#     # Proceed at your own risk.
#     do_checksum_check = True

#     field_name = 'file'
#     content_range_pattern = re.compile(
#         r'^bytes (?P<start>\d+)-(?P<end>\d+)/(?P<total>\d+)$'
#     )
#     max_bytes = _settings.MAX_BYTES  # Max amount of data that can be uploaded

#     def on_completion(self, upload, request):
#         """
#         Initiates asynchronous processing for an uploaded file and saves the upload record.

#         This function is likely called after a file upload is completed successfully.
#         It performs the following actions:

#         1. Schedules the `process_upload` Celery task asynchronously to process the uploaded file.
#         2. Creates or retrieves a `TaskMeta` object associated with the upload, linking it
#         to the task ID for tracking purposes.
#         3. Saves the updated `Upload` object to the database, including the task ID relationship.

#         Args:
#             upload (Upload object): The uploaded file object.
#             request (HttpRequest): The Django request object (may or may not be used).
#         """

#         result = process_upload.delay(str(upload.id))
#         upload.task, created = TaskMeta.objects.get_or_create(
#             task_id=result.task_id)
#         upload.save()

#     def get_max_bytes(self, request):
#         """
#         Used to limit the max amount of data that can be uploaded. `None` means
#         no limit.
#         You can override this to have a custom `max_bytes`, e.g. based on
#         logged user.
#         """

#         return self.max_bytes

#     def is_valid_chunked_upload(self, chunked_upload):
#         """
#         Check if chunked upload has already expired or is already complete.
#         """
#         if chunked_upload.expired:
#             raise ChunkedUploadError(status=status.HTTP_410_GONE,
#                                      detail='Upload has expired')
#         error_msg = 'Upload has already been marked as "%s"'
#         if chunked_upload.status == chunked_upload.COMPLETE:
#             raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
#                                      detail=error_msg % 'complete')

#     def _put_chunk(self, request, pk=None, whole=False, *args, **kwargs):
#         try:
#             chunk = request.data[self.field_name]
#         except KeyError:
#             raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
#                                      detail='No chunk file was submitted')

#         if whole:
#             start = 0
#             total = chunk.size
#             end = total - 1
#         else:
#             content_range = request.META.get('HTTP_CONTENT_RANGE', '')
#             match = self.content_range_pattern.match(content_range)
#             if not match:
#                 raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
#                                          detail='Error in request headers')

#             start = int(match.group('start'))
#             end = int(match.group('end'))
#             total = int(match.group('total'))

#         chunk_size = end - start + 1
#         max_bytes = self.get_max_bytes(request)

#         if end > total:
#             raise ChunkedUploadError(
#                 status=status.HTTP_400_BAD_REQUEST,
#                 detail='End of chunk exceeds reported total (%s bytes)' % total
#             )

#         if max_bytes is not None and total > max_bytes:
#             raise ChunkedUploadError(
#                 status=status.HTTP_400_BAD_REQUEST,
#                 detail='Size of file exceeds the limit (%s bytes)' % max_bytes
#             )

#         if chunk.size != chunk_size:
#             raise ChunkedUploadError(
#                 status=status.HTTP_400_BAD_REQUEST,
#                 detail="File size doesn't match headers: file size is {} but {} reported".format(
#                     chunk.size,
#                     chunk_size,
#                 ),
#             )

#         if pk:
#             upload_id = pk
#             chunked_upload = get_object_or_404(self.get_queryset(),
#                                                pk=upload_id)
#             self.is_valid_chunked_upload(chunked_upload)
#             if chunked_upload.offset != start:
#                 raise ChunkedUploadError(
#                     status=status.HTTP_400_BAD_REQUEST,
#                     detail='Offsets do not match',
#                     expected_offset=chunked_upload.offset,
#                     provided_offset=start,
#                 )

#             chunked_upload.append_chunk(chunk, chunk_size=chunk_size)
#         else:
#             kwargs = {'offset': chunk.size}

#             if hasattr(self.model, self.user_field_name):
#                 if hasattr(request, 'user') and request.user.is_authenticated:
#                     kwargs[self.user_field_name] = request.user
#                 elif self.model._meta.get_field(self.user_field_name).null:
#                     kwargs[self.user_field_name] = None
#                 else:
#                     raise ChunkedUploadError(
#                         status=status.HTTP_400_BAD_REQUEST,
#                         detail="Upload requires user authentication but user cannot be determined",
#                     )

#             chunked_upload = self.serializer_class(data=request.data)
#             if not chunked_upload.is_valid():
#                 raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
#                                          detail=chunked_upload.errors)

#             # chunked_upload is currently a serializer;
#             # save returns model instance
#             chunked_upload = chunked_upload.save(**kwargs)

#         return chunked_upload

#     def handle_put(self, request, pk=None, *args, **kwargs):
#         task = process_upload_chunk.delay(request.data, pk=pk, *args, **kwargs)
#         return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)

#     def checksum_check(self, chunked_upload, checksum):
#         """
#         Verify if checksum sent by client matches generated checksum.
#         """
#         if chunked_upload.checksum != checksum:
#             raise ChunkedUploadError(status=status.HTTP_400_BAD_REQUEST,
#                                      detail='checksum does not match')

#     def handle_post(self, request, pk=None, *args, **kwargs) -> Response:
#         # If pk is provided, use it as the upload_id
#         upload_id = pk

#         # If pk is not provided, handle chunked upload asynchronously
#         if not pk:
#             async_result = process_upload_chunk.delay(
#                 request.data, whole=True, **kwargs)
#             return Response({"task_id": async_result.id}, status=status.HTTP_202_ACCEPTED)

#         # Check if checksum is provided
#         checksum = request.data.get(_settings.CHECKSUM_TYPE)
#         if self.do_checksum_check and not checksum:
#             raise ChunkedUploadError(
#                 status=status.HTTP_400_BAD_REQUEST,
#                 detail="Checksum of type '{}' is required".format(
#                     _settings.CHECKSUM_TYPE),
#             )

#         # Get the corresponding object if chunked_upload is not None
#         chunked_upload = get_object_or_404(self.get_queryset(), pk=upload_id)

#         # Validate the chunked upload
#         self.is_valid_chunked_upload(chunked_upload)

#         # Perform checksum check if required
#         if self.do_checksum_check:
#             if should_use_celery(chunked_upload.file.size):
#                 task = checksum_check.delay(chunked_upload, checksum)
#                 return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
#             else:
#                 self.checksum_check(chunked_upload, checksum)

#         # Handle completion
#         return self.on_completion(chunked_upload, request)

#     @method_decorator(cache_page(0))
#     def _get(self, request, pk=None, *args, **kwargs):
#         if pk:
#             return self.retrieve(request, pk=pk, *args, **kwargs)
#         else:
#             return self.list(request, *args, **kwargs)
