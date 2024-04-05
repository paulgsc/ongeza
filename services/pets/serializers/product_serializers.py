from rest_framework import serializers
from pets.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        field = '__all__'
