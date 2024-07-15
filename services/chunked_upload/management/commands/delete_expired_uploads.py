
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.utils import timezone
from services.settings.upload import EXPIRATION_DELTA
from chunked_upload.models import ChunkedUpload


class Command(BaseCommand):

    # Has to be a ChunkedUpload subclass
    model = ChunkedUpload

    help = 'Deletes chunked uploads that have already expired.'

    def handle(self, *args, **options):

        qs = self.model.objects.all()
        qs = qs.filter(created_on__lt=(timezone.now() -
                       EXPIRATION_DELTA) | Q(status=ChunkedUpload.ARCHIVED))

        for chunked_upload in qs:
            # Deleting objects individually to call delete method explicitly
            chunked_upload.delete()
