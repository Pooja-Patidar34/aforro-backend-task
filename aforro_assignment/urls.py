from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from orders.views import OrderViewSet, create_order_view
from stores.views import StoreViewSet, InventoryViewSet
from search.views import ProductSearchViewSet

router = DefaultRouter()
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'search/products', ProductSearchViewSet, basename='product-search')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('orders/', create_order_view, name='create-order'),
    re_path(r'^stores/(?P<store_id>\d+)/orders/$', OrderViewSet.as_view({'get': 'list'}), name='store-orders'),
    re_path(r'^stores/(?P<store_id>\d+)/inventory/$', InventoryViewSet.as_view({'get': 'list'}), name='store-inventory'),
    path('api/search/products/', ProductSearchViewSet.as_view({'get': 'search'}), name='search-products'),
    path('api/search/suggest/', ProductSearchViewSet.as_view({'get': 'suggest'}), name='autocomplete'),

    # Swagger/OpenAPI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
