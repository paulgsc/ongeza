"""
Serializer Registry

This module provides a registry for storing model-specific serializers.

Example Usage:
    registry = SerializerRegistry()

    # Registering serializers
    registry.register_serializer('book', BookSerializer)
    registry.register_serializer('author', AuthorSerializer)
    registry.register_serializer('publisher', PublisherSerializer)

    # Example usage
    book_data = {'title': 'Example Book', 'author': 'John Doe'}
    book_serializer = registry.get_serializer_class('book')
    serialized_book = book_serializer(data=book_data)
    if serialized_book.is_valid():
        serialized_book.save()
    else:
        print("Error:", serialized_book.errors)
"""

from typing import Type, Dict
from rest_framework import serializers


class SerializerRegistry:
    """
    A registry for storing model-specific serializers.
    """

    def __init__(self):
        self.registry: Dict[str, Type[serializers.ModelSerializer]] = {}

    def register_serializer(self, model_name: str, serializer_class: Type[serializers.ModelSerializer]):
        """
        Register a serializer class for a given model name.

        Args:
            model_name (str): The name of the model.
            serializer_class (Type[serializers.ModelSerializer]): The serializer class to register.
        """
        self.registry[model_name] = serializer_class

    def get_serializer_class(self, model_name: str) -> Type[serializers.ModelSerializer]:
        """
        Get the serializer class for a given model name.

        Args:
            model_name (str): The name of the model.

        Returns:
            Type[serializers.ModelSerializer]: The serializer class.

        Raises:
            ValueError: If no serializer is registered for the provided model name.
        """
        try:
            return self.registry[model_name]
        except KeyError:
            raise ValueError(
                f"No serializer registered for model '{model_name}'")

    def serialize_data(self, model_name: str, instance, **kwargs):
        """
        Serialize data for a given model instance using the registered serializer.

        Args:
            model_name (str): The name of the model.
            instance: The model instance to serialize.
            **kwargs: Additional keyword arguments to pass to the serializer.

        Returns:
            dict: The serialized data.
        """
        serializer_class = self.get_serializer_class(model_name)
        serializer = serializer_class(instance=instance, **kwargs)
        return serializer.data

    def update_instance(self, model_name: str, instance, validated_data, **kwargs):
        """
        Update a model instance with validated data using the registered serializer.

        Args:
            model_name (str): The name of the model.
            instance: The model instance to update.
            validated_data: The validated data to update the instance with.
            **kwargs: Additional keyword arguments to pass to the serializer.

        Returns:
            Any: The updated model instance.

        Raises:
            ValueError: If the serializer is not valid.
        """
        serializer_class = self.get_serializer_class(model_name)
        serializer = serializer_class(
            instance=instance, data=validated_data, **kwargs)
        if serializer.is_valid():
            serializer.save()
            return serializer.instance
        else:
            raise ValueError(serializer.errors)

    def create_instance(self, model_name: str, validated_data, **kwargs):
        """
        Create a new model instance using the registered serializer.

        Args:
            model_name (str): The name of the model.
            validated_data: The validated data to create the instance with.
            **kwargs: Additional keyword arguments to pass to the serializer.

        Returns:
            Any: The created model instance.

        Raises:
            ValueError: If the serializer is not valid.
        """
        serializer_class = self.get_serializer_class(model_name)
        serializer = serializer_class(data=validated_data, **kwargs)
        if serializer.is_valid():
            serializer.save()
            return serializer.instance
        else:
            raise ValueError(serializer.errors)
