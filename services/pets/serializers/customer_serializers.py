# serializers.py

from rest_framework import serializers
from pets.models import Customer
from common.serializers.registry_serializers import RedisSerializerRegistry

# Define serializers for each model


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


# Function to register serializers with the registry
def register_serializers():
    print('mahomeboy')
    # Instantiate RedisSerializerRegistry
    registry = RedisSerializerRegistry()

    # Register serializers with the registry
    registry.register_serializer('customer', CustomerSerializer)


# Entry point when the module is run as the main program
if __name__ == "__main__":
    register_serializers()
