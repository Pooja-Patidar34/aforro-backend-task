from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from stores.models import Store, Inventory
from products.models import Product
from .tasks import send_order_confirmation


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        if store_id:
            return Order.objects.filter(store_id=store_id).prefetch_related('items')
        return Order.objects.prefetch_related('items')

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        store_id = serializer.validated_data['store_id']
        items_data = serializer.validated_data['items']

        store = get_object_or_404(Store, id=store_id)

        try:
            with transaction.atomic():
                all_available = True
                inventory_checks = []

                for item in items_data:
                    product_id = item.get('product_id')
                    quantity = item.get('quantity_requested')

                    product = get_object_or_404(Product, id=product_id)
                    inventory = Inventory.objects.filter(store=store, product=product).first()

                    if not inventory or inventory.quantity < quantity:
                        all_available = False
                        break

                    inventory_checks.append((inventory, quantity))

                order = Order.objects.create(
                    store=store,
                    status='CONFIRMED' if all_available else 'REJECTED'
                )

                for item in items_data:
                    product_id = item.get('product_id')
                    quantity = item.get('quantity_requested')
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity_requested=quantity
                    )

                if all_available:
                    for inventory, quantity in inventory_checks:
                        inventory.quantity -= quantity
                        inventory.save()

                    send_order_confirmation.delay(order.id)

                order_serializer = OrderSerializer(order)
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


from rest_framework.decorators import api_view

@api_view(['POST'])
def create_order_view(request):
    """Standalone view for creating orders"""
    serializer = OrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    store_id = serializer.validated_data['store_id']
    items_data = serializer.validated_data['items']

    store = get_object_or_404(Store, id=store_id)

    try:
        with transaction.atomic():
            all_available = True
            inventory_checks = []

            for item in items_data:
                product_id = item.get('product_id')
                quantity = item.get('quantity_requested')

                product = get_object_or_404(Product, id=product_id)
                inventory = Inventory.objects.filter(store=store, product=product).first()

                if not inventory or inventory.quantity < quantity:
                    all_available = False
                    break

                inventory_checks.append((inventory, quantity))

            order = Order.objects.create(
                store=store,
                status='CONFIRMED' if all_available else 'REJECTED'
            )

            for item in items_data:
                product_id = item.get('product_id')
                quantity = item.get('quantity_requested')
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity_requested=quantity
                )

            if all_available:
                for inventory, quantity in inventory_checks:
                    inventory.quantity -= quantity
                    inventory.save()

                try:
                    send_order_confirmation.delay(order.id)
                except Exception:
                    pass  # Celery task failed, but order still created

            order_serializer = OrderSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
