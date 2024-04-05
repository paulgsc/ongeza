"""
    pets views
"""

from rest_framework.response import Response
from rest_framework.views import APIView
from django.apps import apps
from common.serializers.registry_serializers import RedisSerializerRegistry
from common.serializers.field_meta_serializers import FieldMetaSerializer
# Create your views here.


class PetsModelNamesView(APIView):
    """
    A view to retrieve a list of all model names in the Django app.
    """
    # TODO : Add permission, and access policy

    def get(self, request):
        """
        Retrieves a list of all model names and returns it as a JSON response.

        Args:
            request: The HTTP request.

        Returns:
            Response: JSON response containing the list of model names.
        """
        # Get the app config for the 'pets' app
        pets_app_config = apps.get_app_config('pets')

        # Get all installed models in the Django app
        installed_models = pets_app_config.get_models()

        # Extract the model names from the installed models
        model_names = [model.__name__ for model in installed_models]

        # Return the list of model names as a JSON response
        return Response(model_names)


class ModelFieldsView(APIView):
    """
    A view to retrieve metadata about fields of a specified model.
    """
    # TODO : Add permission, and access policy

    def get(self, request):
        """
        Retrieves metadata about fields of a specified model and returns it as a JSON response.

        Args:
            request: The HTTP request.

        Returns:
            Response: JSON response containing the field metadata.
        """
        registry = RedisSerializerRegistry()
        model_name = request.query_params.get('model', None)
        if not model_name:
            return Response({'error': 'Model name not provided'}, status=400)
        try:
            serializer_class = registry.get_serializer_class(
                model_name=model_name)
        except ValueError as e:
            return Response({'error': str(e)}, status=500)
        serialized_data = FieldMetaSerializer().get_serializer_fields_meta(
            serializer_class=serializer_class)
        return Response(serialized_data, status=200)
