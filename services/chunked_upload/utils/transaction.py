from __future__ import absolute_import
from functools import wraps
from celery import current_task, shared_task
from celery.states import STARTED
from celery.contrib.abortable import AbortableTask

from django.db import transaction
from chunked_upload.models import ChunkedUpload
from utils.exceptions import AbortedError


# this is just adding the if_aborted method to AbortableTask

class CustomAbortableTask(AbortableTask):
    """Extends Celery's AbortableTask with a method to check and raise AbortedError."""

    abstract = True  # Prevent direct instantiation

    def run(self, *args, **kwargs):
        """Override the run method inherited from AbortableTask."""
        raise NotImplementedError("Subclasses must implement the run method")

    def if_aborted(self):
        """Raises AbortedError if the task has been aborted."""
        if self.is_aborted():
            raise AbortedError("Task aborted")


# this is a reusable decorator used to create abortable celery tasks


def abortable_task(funct):
    # we need to wrap the task callable with the boilerplate
    # to handle the setup stuff related to allowing aborts
    @wraps(funct)
    def task_wrapper(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        try:
            # check if aborted before doing anything
            # if so, this will raise Aborted Error
            self.if_aborted()
            # if not aborted set to started
            # FIXUP: this seems to be a race condition
            self.update_state(state=STARTED)

            # Enforce instance type if instance is provided
            if instance and not isinstance(instance, ChunkedUpload):
                raise AbortedError("Instance must be an instance of YourModel")

            # call the task function
            ret = funct(self, *args, **kwargs)
        except AbortedError:
            return "Task Aborted"
        return ret
    # celery uses the function name to identify tasks at creation
    # so we need to "change" the name of our wrapper function to
    # match the callable we want to be a task
    task_wrapper.__name__ = funct.__name__
    # return the callable wrapped in task_wrapper, but add
    # the shared task decorator with the AbortableTask base
    return shared_task(task_wrapper, bind=True, base=CustomAbortableTask)


# we define our own atomic decorator that will check if the task
# is aborted before exiting the transaction, and if true rollback
# by raising an AbortedException
def atomic_with_abortion(funct):
    def abort_wrapper(*args, **kwargs):
        ret = funct(*args, **kwargs)
        if current_task and hasattr(current_task, "if_aborted"):
            current_task.if_aborted()
        return ret
    return transaction.atomic(abort_wrapper)
