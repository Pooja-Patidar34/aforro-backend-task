from django.db import models
from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_title', 'product_price', 'quantity_requested']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'store', 'status', 'created_at', 'items', 'total_items']
        read_only_fields = ['created_at', 'status']

    def get_total_items(self, obj):
        return obj.items.aggregate(total=models.Sum('quantity_requested'))['total'] or 0


class OrderCreateSerializer(serializers.Serializer):
    store_id = serializers.IntegerField()
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(),
            required=True
        )
    )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('At least one item is required.')
        return value
