from .customer_serializers import CustomerSerializer
from .category_serializers import CategorySerializer
from .order_serializers import OrderSerializer
from .orderline_serializers import OrderLineSerializer
from .product_serializers import ProductSerializer
from common.serializers.registry_serializers import RedisSerializerRegistry

# Function to register serializers with the registry


def register_serializers():
    # Instantiate RedisSerializerRegistry
    registry = RedisSerializerRegistry()

    # Register serializers with the registry
    registry.register_serializer('customer', CustomerSerializer)
    registry.register_serializer('category', CategorySerializer)
    registry.register_serializer('product', ProductSerializer)
    registry.register_serializer('order', OrderSerializer)
    registry.register_serializer('orderline', OrderLineSerializer)


# Entry point when the module is run as the main program
if __name__ == "__main__":
    register_serializers()
