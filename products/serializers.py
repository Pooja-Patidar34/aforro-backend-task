from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'category_name', 'created_at']
        read_only_fields = ['created_at']


class ProductSearchSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    inventory_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category_name', 'inventory_quantity']

    def get_inventory_quantity(self, obj):
        store_id = self.context.get('store_id')
        if store_id:
            inventory = obj.inventory.filter(store_id=store_id).first()
            return inventory.quantity if inventory else 0
        return None
