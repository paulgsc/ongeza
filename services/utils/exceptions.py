"""
Exceptions raised by django-chunked-upload.
"""


class ChunkedUploadError(Exception):
    """
    Exception raised if errors in the request/process.
    """

    def __init__(self, status, **data):
        self.status_code = status
        self.data = data


class AbortedError(Exception):
    """
    Indicates that a task or process has been aborted prematurely.

    This exception is raised when the execution of a task or process
    is intentionally interrupted before completion. This could be due to
    various reasons, such as user cancellation, timeouts, external events,
    or error conditions that require termination.
    """


class RedisPubSubError(Exception):
    """
    Indicates an error related to Redis Pub/Sub operations.

    This exception is raised when an error occurs during Redis
    Pub/Sub operations, such as subscribing, publishing, or listening
    to channels. It can be raised due to various reasons, including
    network issues, authentication failures, or invalid operations.
    """
