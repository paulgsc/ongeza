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

import json
import os
from typing import Type
from functools import lru_cache
from rest_framework import serializers
from django.utils.module_loading import import_string
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class SerializerRegistry:
    """
    A registry for storing model-specific serializers.
    """

    _instance = None
    registry = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.load_serializers()
            cls._instance.load_serializers()
        return cls._instance

    @classmethod
    def load_serializers(cls):
        """
        Load serializers from JSON files in the serializers_config directory.
        """
        serializers_config_dir = getattr(
            settings, 'SERIALIZERS_CONFIG_DIR', None)
        if not serializers_config_dir:
            raise ImproperlyConfigured(
                'SERIALIZERS_CONFIG_DIR setting is not defined.')

        for filename in os.listdir(serializers_config_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(serializers_config_dir, filename)
                with open(file_path, 'r') as f:
                    serializer_configs = json.load(f)

                for config in serializer_configs:
                    model_name = config['model'].lower()
                    serializer_path = config['serializer']
                    try:
                        serializer_module, serializer_class_name = serializer_path.rsplit(
                            '.', 1)
                        serializer_module = import_string(serializer_module)
                        serializer_class = getattr(
                            serializer_module, serializer_class_name)
                        cls.register_serializer(model_name, serializer_class)
                    except (ImportError, AttributeError) as e:
                        raise ValueError(
                            f"Error loading serializer for model '{model_name}': {e}")

    def register_serializer(self, model_name: str, serializer_class: Type[serializers.ModelSerializer]):
        """
        Register a serializer class for a given model name.

        Args:
            model_name (str): The name of the model.
            serializer_class (Type[serializers.ModelSerializer]): The serializer class to register.
        """
        self.registry[model_name] = serializer_class

    @classmethod
    @lru_cache(maxsize=None)
    def get_serializer_class(cls, model_name: str) -> Type[serializers.ModelSerializer]:
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
            return cls.registry[model_name]
        except KeyError as exc:
            raise ValueError(
                f"No serializer registered for model '{model_name}'") from exc

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
