"""
Module providing custom serializers for formatting data fields.
"""

import datetime
import decimal
from rest_framework import serializers

class FormattedFieldSerializer(serializers.Field):
    """
    Base class for formatting serializer fields.

    Subclasses must override the `formatter` method to provide specific formatting logic.

    Example:
        Consider a scenario where you have a model `Product` with a field `price` representing
        the price of the product. You can use `MonetaryFieldSerializer` to format the price
        into a currency representation.

        ```python
        from rest_framework import serializers
        from .models import Product

        class ProductSerializer(serializers.ModelSerializer):
            price = MonetaryFieldSerializer()

            class Meta:
                model = Product
                fields = ['name', 'price']
        ```

        In this example, the `price` field of the `ProductSerializer` will use the
        `MonetaryFieldSerializer` to format the price value.

    """
    def formatter(self, value):
        """
        Method to be overridden by subclasses for formatting the field value.

        Args:
            value: The value of the field.

        Raises:
            NotImplementedError: This method must be overridden by subclasses.

        Returns:
            Any: The formatted representation of the field's value.
        """
        raise NotImplementedError("Subclasses must override the 'formatter' method.")

    def to_representation(self, value):
        """
        Convert the field's value into a representation suitable for serialization.

        Args:
            value: The value of the field.

        Returns:
            str: The formatted representation of the field's value.
        """
        return self.formatter(value)

    def to_internal_value(self, data):
        """
        Convert the serialized data into internal value.

        Args:
            data: Serialized data.

        Returns:
            Any: Internal value of the data.
        """
        return data

class MonetaryFieldSerializer(FormattedFieldSerializer, serializers.DecimalField):
    """
    Serializer for formatting currency to dollars.
    """
    def formatter(self, value):
        """
        Format the amount into currency.

        Args:
            value: The amount to be formatted.

        Returns:
            str: The formatted currency value.
        """
        amount = decimal.Decimal(value)
        amount = amount.quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_HALF_UP)
        amount_str = '{:,.2f}'.format(amount)
        return '$' + amount_str

class DateFieldSerializer(FormattedFieldSerializer, serializers.DateTimeField):
    """
    Serializer for formatting date and time to a string representation.
    """
    def formatter(self, value):
        """
        Format the date and time into a string representation.

        Args:
            value: The date and time to be formatted.

        Returns:
            str: The formatted date and time string.
        """
        if isinstance(value, datetime.datetime):
            value = value.astimezone()
        return value.strftime('%b %d %Y at %I:%M %p')


class MaskedFieldSerializer(FormattedFieldSerializer, serializers.CharField):
    """
    Serializer for masking sensitive data.
    """
    def formatter(self, value):
        """
        Mask sensitive data by replacing all characters with asterisks.

        Args:
            value: The sensitive data to be masked.

        Returns:
            str: The masked data.
        """
        return '*' * len(str(value))

class PercentageFieldSerializer(FormattedFieldSerializer, serializers.DecimalField):
    """
    Serializer for formatting decimal values as percentages.
    """
    def formatter(self, value):
        """
        Format the decimal value as a percentage.

        Args:
            value: The decimal value to be formatted.

        Returns:
            str: The formatted percentage value.
        """
        percentage = decimal.Decimal(value) * 100
        return '{:.2f}%'.format(percentage)


class BooleanFieldSerializer(FormattedFieldSerializer, serializers.BooleanField):
    """
    Serializer for formatting boolean values.
    """
    def formatter(self, value):
        """
        Format the boolean value.

        Args:
            value: The boolean value to be formatted.

        Returns:
            str: The formatted boolean value.
        """
        return 'True' if value else 'False'


class DurationFieldSerializer(FormattedFieldSerializer, serializers.DurationField):
    """
    Serializer for formatting durations.
    """
    def formatter(self, value):
        """
        Format the duration in a human-readable format.

        Args:
            value: The duration value to be formatted.

        Returns:
            str: The formatted duration string.
        """
        return str(value)
