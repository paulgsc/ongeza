from rest_framework import serializers


class FieldMetaSerializer(serializers.Serializer):
    """
    Serializer to return field metadata for a given model serializer.
    """
    name = serializers.CharField()
    label = serializers.CharField(allow_blank=True)
    help_text = serializers.CharField(allow_blank=True)
    required = serializers.BooleanField()
    read_only = serializers.BooleanField()
    write_only = serializers.BooleanField()
    field_type = serializers.CharField()

    @staticmethod
    def get_field_meta(field):
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

    def to_representation(self, instance):
        """
        Convert the field instance to a dictionary representation.
        """
        return FieldMetaSerializer.get_field_meta(instance)

    @classmethod
    def get_serializer_fields_meta(cls, serializer_class):
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

    def create(self, validated_data):
        raise serializers.ValidationError(
            "Creation not allowed for this resource.")

    def update(self, instance, validated_data):
        raise serializers.ValidationError(
            "Update not allowed for this resource.")


class ReadOnlyWithMetadataSerializer(ReadOnlyBaseSerializer):
    """
    Custom model serializer that includes field metadata in the serialized data.
    """
    is_read_only = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self.context.get('list_retrieval'):
            data = self.add_field_meta(instance, data)
        return data

    def get_is_read_only(self, instance):
        """
        Get the read-only status of the serializer.
        """
        return True

    @staticmethod
    def get_field_info(field):
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

    def add_field_meta(self, instance, data):
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
