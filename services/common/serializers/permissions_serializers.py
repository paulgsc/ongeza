"""
Permission Serializer Module

This module contains custom serializer classes related to permissions in the application.
"""

from rest_framework import serializers

class ReadOnlyField(serializers.Field):
    """
    A read-only field that raises an error if an attempt is made to modify its value.

    This field is useful for marking certain fields in a serializer as read-only,
    preventing them from being updated when performing write operations.

    Example:
    ```
    from rest_framework import serializers

    class ProductSerializer(serializers.ModelSerializer):
        sku = ReadOnlyField()

        class Meta:
            model = Product
            fields = '__all__'
    ```
    In this example, the 'sku' field of the `ProductSerializer` is marked as read-only.
    """

    def to_internal_value(self, data):
        """
        Validate the incoming data.

        If the parent instance is not None, raise a validation error indicating that
        the field is read-only.
        """
        if self.parent.instance is not None:
            raise serializers.ValidationError({'field_name': 'This field is read-only.'})
        return data
