"""
Module providing custom serializers for formatting data fields.

"""

import datetime
import decimal
from rest_framework import serializers


def format_currency(value):
    """
    Format the amount into currency.

    Args:
        value: The amount to be formatted.

    Returns:
        str: The formatted currency value.
    """
    amount = decimal.Decimal(value)
    amount = amount.quantize(decimal.Decimal(
        '.01'), rounding=decimal.ROUND_HALF_UP)
    amount_str = '{:,.2f}'.format(amount)
    return '$' + amount_str


def format_date(value):
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


def format_masked(value):
    """
    Mask sensitive data by replacing all characters with asterisks.

    Args:
        value: The sensitive data to be masked.

    Returns:
        str: The masked data.
    """
    return '*' * len(str(value))


def format_percentage(value):
    """
    Format the decimal value as a percentage.

    Args:
        value: The decimal value to be formatted.

    Returns:
        str: The formatted percentage value.
    """
    percentage = decimal.Decimal(value) * 100
    return '{:.2f}%'.format(percentage)


def format_boolean(value):
    """
    Format the boolean value.

    Args:
        value: The boolean value to be formatted.

    Returns:
        str: The formatted boolean value.
    """
    return 'True' if value else 'False'


def format_duration(value):
    """
    Format the duration in a human-readable format.

    Args:
        value: The duration value to be formatted.

    Returns:
        str: The formatted duration string.
    """
    return str(value)


class FormattedField(serializers.Field):
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
              price = FormattedField(format='currency')
              created_at = FormattedField(format='date')

              class Meta:
                  model = Product
                  fields = ['name', 'price', 'created_at']
          ```

          In this example, the `price` field of the `ProductSerializer` will use the
          `MonetaryFieldSerializer` to format the price value.
  """

    def __init__(self, formt=None, **kwargs):
        self.formt = formt
        super().__init__(**kwargs)

    def to_representation(self, value):
        format_function = getattr(self, 'format_' + self.formt, None)
        if format_function:
            return format_function(value)
        return value
