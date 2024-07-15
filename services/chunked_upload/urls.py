"""
URL patterns for handling file-related views.

This module defines URL patterns for file-related views using Django's path function.

Attributes:
    file_list (callable): A view function that handles HTTP GET (list) and POST (create) requests for files.
    file_detail (callable): A view function that handles HTTP GET (retrieve), PUT (update), PATCH (partial_update),
        and DELETE (destroy) requests for a specific file identified by its UUID.
    file_download (callable): A view function that handles HTTP GET requests to download a specific file identified
        by its UUID.
    file_patterns (list): A list of URL patterns for file-related views, including listing files, retrieving,
        updating, and deleting a specific file, and downloading a file.
    file_patterns_no_id (list): A list of URL patterns for file-related views, excluding the UUID identifier
        in the URL. Useful for operations not specific to a single file.

Examples:
    urlpatterns = [
        path('', include('file_patterns')),
        # Add other URL patterns as needed
    ]
"""


from django.urls import path
from chunked_upload.views.upload import ChunkedUploadView

urlpatterns = [
    # POST endpoint for creating new uploads
    path('create_file/', ChunkedUploadView.as_view(), name='chunked-upload'),
    # PUT endpoint for updating existing uploads
    path('add_file_chunk/<int:pk>/', ChunkedUploadView.as_view(),
         name='chunked-upload-update'),
]
