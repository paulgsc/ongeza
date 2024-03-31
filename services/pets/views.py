"""
    pets views
"""

from rest_framework.response import Response
from rest_framework.views import APIView
from django.apps import apps

# Create your views here.


class ModelFieldsView(APIView):

    def get(self, request):
        model_data = []

        for model in apps.get_models():
            if hasattr(model, 'can_be_featured') and model.can_be_featured():
                model_name = model.__name__
                record_count = model.objects.count()
                model_data.append(
                    {'name': model_name, 'record_count': record_count})
        return Response(model_data, status=200)


class MyModelFieldMetaView(APIView):
    """
    View to retrieve metadata for fields of a model.
    """

    def get(self, request, *args, **kwargs):
        # Instantiate the serializer for the model
        serializer = MyModelSerializer()

        # Get metadata for all fields in the serializer
        fields_meta = FieldMetaSerializer.get_serializer_fields_meta(
            serializer)

        return Response(fields_meta)
