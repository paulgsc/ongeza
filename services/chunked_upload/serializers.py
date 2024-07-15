from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import ChunkedUpload


class ChunkedUploadSerializer(serializers.ModelSerializer):
    viewname = 'chunkedupload-detail'
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse(self.viewname,
                       kwargs={'pk': obj.id},
                       request=self.context['request'])

    class Meta:
        model = ChunkedUpload
        fields = '__all__'
        read_only_fields = ('status', 'completed_at')


class ChunkedUploadReadOnlySerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = ChunkedUpload
        exclude = ['id', 'file', 'offset']
        read_only_fields = '__all__'

    def get_file_size(self, obj):
        return obj.file.size if obj.file else None
