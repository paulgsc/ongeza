from .customer_serializers import CustomerSerializer, RedisSerializerRegistry
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
