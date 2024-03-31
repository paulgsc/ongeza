# """
# URL patterns for handling file-related views.

# This module defines URL patterns for file-related views using Django's path function.

# Attributes:
#     file_list (callable): A view function that handles HTTP GET (list) and POST (create) requests for files.
#     file_detail (callable): A view function that handles HTTP GET (retrieve), PUT (update), PATCH (partial_update),
#         and DELETE (destroy) requests for a specific file identified by its UUID.
#     file_download (callable): A view function that handles HTTP GET requests to download a specific file identified
#         by its UUID.
#     file_patterns (list): A list of URL patterns for file-related views, including listing files, retrieving,
#         updating, and deleting a specific file, and downloading a file.
#     file_patterns_no_id (list): A list of URL patterns for file-related views, excluding the UUID identifier
#         in the URL. Useful for operations not specific to a single file.

# Examples:
#     urlpatterns = [
#         path('', include('file_patterns')),
#         # Add other URL patterns as needed
#     ]
# """


# from django.urls import path


# file_list = data_views.FileViewSet.as_view({
#     "get": "list",
#     "post": "create"
# })
# file_detail = data_views.FileViewSet.as_view({
#     "get": "retrieve",
#     "put": "update",
#     "patch": "partial_update",
#     "delete": "destroy"
# })
# file_download = data_views.FileViewSet.as_view({
#     "get": "download",
# })

# download_list = views.DownloadViewSet.as_view({
#     "get": "list",
# })
# download_detail = views.DownloadViewSet.as_view({
#     "get": "retrieve",
# })


# file_patterns = [
#     path('', file_list, name='list'),
#     path('<uuid:pk>/', file_detail, name='detail'),
#     path('<uuid:pk>/download/', file_download, name='download'),
# ]

# file_patterns_no_id = [
#     path('', file_detail, name='detail'),
#     path('download/', file_download, name='download'),
# ]


# upload_patterns = [
#     path('uploads/', views.UploadView.as_view(), name='upload-list'),
#     path('uploads/<uuid:pk>/', views.UploadView.as_view(), name='upload-detail'),
#     path('uploads/<uuid:pk>/cancel/', views.cancel_upload, name='upload-cancel'),
# ]
