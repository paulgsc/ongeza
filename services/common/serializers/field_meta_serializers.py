"""
This module provides serializers for handling field metadata and read-only operations
with Django REST Framework.

Classes:
- FieldMetaSerializer: A serializer for returning field metadata for a given model serializer.
- ReadOnlyBaseSerializer: A base serializer for read-only operations.
- ReadOnlyWithMetadataSerializer: A custom model serializer that includes field metadata
  in the serialized data.

Usage:
1. FieldMetaSerializer:
   - Use the `get_serializer_fields_meta` method to retrieve field metadata for all fields
     in a given serializer class.

2. ReadOnlyBaseSerializer:
   - Inherit from this class to create read-only serializers.
   - The `create` and `update` methods are overridden to raise a ValidationError,
     preventing creation and update operations.

3. ReadOnlyWithMetadataSerializer:
   - Inherit from this class to create read-only serializers with field metadata included
     in the serialized data.
   - The `to_representation` method is overridden to add field metadata to the serialized data.
   - The `add_field_meta` method is responsible for adding the field metadata to the serialized data.
   - The `get_field_info` method returns a dictionary containing field information for a given field.

Note: Both `ReadOnlyBaseSerializer` and `ReadOnlyWithMetadataSerializer` are abstract base classes
and should be subclassed to create concrete serializer classes.

"""

from typing import Any, Dict, List

from rest_framework import serializers

class FieldMetaSerializer(serializers.Serializer):
    """
    Serializer to return field metadata for a given model serializer.
    """
    name: serializers.CharField = serializers.CharField()
    label: serializers.CharField = serializers.CharField(allow_blank=True)
    help_text: serializers.CharField = serializers.CharField(allow_blank=True)
    required: serializers.BooleanField = serializers.BooleanField()
    read_only: serializers.BooleanField = serializers.BooleanField()
    write_only: serializers.BooleanField = serializers.BooleanField()
    field_type: serializers.CharField = serializers.CharField()

    @staticmethod
    def get_field_meta(field: serializers.Field) -> Dict[str, Any]:
        """
        Get field metadata dictionary for a given field.
        """
        return {
            'name': field.field_name,
            'label': field.label,
            'help_text': field.help_text,
            'required': field.required,
            'read_only': field.read_only,
            'write_only': field.write_only,
            'field_type': field.__class__.__name__,
        }

    def to_representation(self, instance: serializers.Field) -> Dict[str, Any]:
        """
        Convert the field instance to a dictionary representation.
        """
        return FieldMetaSerializer.get_field_meta(instance)

    @classmethod
    def get_serializer_fields_meta(cls, serializer_class: serializers.Serializer) -> List[Dict[str, Any]]:
        """
        Get field metadata for all fields in the given serializer class.
        """
        fields_meta = []
        for field_name, field in serializer_class().fields.items():
            field_meta = FieldMetaSerializer(instance=field)
            fields_meta.append(field_meta.data)
        return fields_meta


class ReadOnlyBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for read-only operations.
    """
    class Meta:
        abstract = True

    def create(self, validated_data: Dict[str, Any]) -> None:
        raise serializers.ValidationError(
            "Creation not allowed for this resource.")

    def update(self, instance: Any, validated_data: Dict[str, Any]) -> None:
        raise serializers.ValidationError(
            "Update not allowed for this resource.")


class ReadOnlyWithMetadataSerializer(ReadOnlyBaseSerializer):
    """
    Custom model serializer that includes field metadata in the serialized data.
    """
    is_read_only: serializers.SerializerMethodField = serializers.SerializerMethodField()


    def to_representation(self, instance: Any) -> Dict[str, Any]:
        data = super().to_representation(instance)
        if not self.context.get('list_retrieval'):
            data = self.add_field_meta(instance, data)
        return data

    def get_is_read_only(self, instance: Any) -> bool:
        """
        Get the read-only status of the serializer.
        """
        return True

    @staticmethod
    def get_field_info(field: serializers.Field) -> Dict[str, Any]:
        """
        Get field information dictionary for a given field.
        """
        return {
            'name': field.field_name,
            'label': field.label,
            'help_text': field.help_text,
            'required': field.required,
            'read_only': field.read_only,
            'write_only': field.write_only,
            'field_type': field.__class__.__name__,
        }

    def add_field_meta(self, instance: Any, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add field metadata to the serialized data.
        """
        updated_data = {}
        for field_name, field in self.fields.items():
            value = field.get_attribute(instance)
            field_info = self.get_field_info(field)
            updated_data[field_name] = {
                "value": value,
                **field_info,
            }
        return updated_data
