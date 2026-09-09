from django.db.models import Q, F, OuterRef, Subquery
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from products.models import Product
from products.serializers import ProductSearchSerializer
from stores.models import Inventory


class SearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductSearchViewSet(viewsets.ViewSet):
    @method_decorator(cache_page(60 * 5))
    def search(self, request):
        query = request.query_params.get('q', '').strip()
        category_id = request.query_params.get('category')
        price_min = request.query_params.get('price_min')
        price_max = request.query_params.get('price_max')
        store_id = request.query_params.get('store_id')
        in_stock = request.query_params.get('in_stock')
        sort = request.query_params.get('sort', 'relevance')

        products = Product.objects.all()

        if query:
            products = products.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )

        if category_id:
            products = products.filter(category_id=category_id)

        if price_min:
            try:
                products = products.filter(price__gte=float(price_min))
            except (ValueError, TypeError):
                pass

        if price_max:
            try:
                products = products.filter(price__lte=float(price_max))
            except (ValueError, TypeError):
                pass

        if in_stock and in_stock.lower() == 'true' and store_id:
            inventory_subquery = Inventory.objects.filter(
                store_id=store_id,
                product=OuterRef('pk')
            )
            products = products.annotate(
                inventory_qty=Subquery(inventory_subquery.values('quantity'))
            ).filter(inventory_qty__gt=0)

        if sort == 'price':
            products = products.order_by('price')
        elif sort == 'newest':
            products = products.order_by('-created_at')
        elif sort == 'relevance' and query:
            from django.db.models import Case, When, IntegerField
            products = products.annotate(
                relevance=Case(
                    When(title__istartswith=query, then=2),
                    default=1,
                    output_field=IntegerField()
                )
            ).order_by('-relevance', '-created_at')

        paginator = SearchPagination()
        paginated_products = paginator.paginate_queryset(products, request)

        serializer = ProductSearchSerializer(
            paginated_products,
            many=True,
            context={'store_id': store_id}
        )

        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='suggest')
    def suggest(self, request):
        q = request.query_params.get('q', '').strip()

        if len(q) < 3:
            return Response({'suggestions': []})

        prefix_matches = Product.objects.filter(
            title__istartswith=q
        ).values_list('title', flat=True).distinct()[:5]

        general_matches = Product.objects.filter(
            title__icontains=q
        ).exclude(
            title__istartswith=q
        ).values_list('title', flat=True).distinct()[:5]

        suggestions = list(prefix_matches) + list(general_matches)
        suggestions = suggestions[:10]

        return Response({'suggestions': suggestions})
