# serializers.py

from rest_framework import serializers
from pets.models import Customer


# Define serializers for each model


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
