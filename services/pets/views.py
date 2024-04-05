"""
    pets views
"""

from rest_framework.response import Response
from rest_framework.views import APIView
from common.serializers.registry_serializers import RedisSerializerRegistry
from common.serializers.field_meta_serializers import FieldMetaSerializer
# Create your views here.


class ModelFieldsView(APIView):
    # TODO : Add permission, and access policy

    def get(self, request):
        registry = RedisSerializerRegistry()
        model_name = request.query_params.get('model', None)
        if not model_name:
            return Response(status=500)
        serializer_class = registry.get_serializer_class(model_name=model_name)
        serialized_data = FieldMetaSerializer().get_serializer_fields_meta(
            serializer_class=serializer_class)
        return Response(serialized_data, status=200)


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
