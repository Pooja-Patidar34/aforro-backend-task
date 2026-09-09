from rest_framework import serializers
from .models import Store, Inventory


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'location']


class InventorySerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    category_name = serializers.CharField(source='product.category.name', read_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'product', 'product_title', 'product_price', 'category_name', 'quantity']
        read_only_fields = ['updated_at']
