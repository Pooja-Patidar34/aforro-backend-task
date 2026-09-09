from rest_framework import viewsets
from .models import Store, Inventory
from .serializers import StoreSerializer, InventorySerializer


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventorySerializer

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        if store_id:
            return Inventory.objects.filter(
                store_id=store_id
            ).select_related('product', 'product__category').order_by('product__title')
        return Inventory.objects.select_related('product', 'product__category')
