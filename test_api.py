#!/usr/bin/env python
"""
Quick API test script to verify endpoints
Run after starting the development server: python manage.py runserver
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aforro_assignment.settings')
django.setup()

from django.test import Client
from products.models import Category, Product
from stores.models import Store, Inventory
from orders.models import Order, OrderItem

def test_endpoints():
    client = Client()

    print("=" * 60)
    print("TESTING AFORRO API ENDPOINTS")
    print("=" * 60)

    # Test 1: List stores
    print("\n1. Testing GET /api/stores/")
    response = client.get('/api/stores/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Stores found: {len(data.get('results', []))}")

    # Test 2: Get first store
    store = Store.objects.first()
    if store:
        print(f"\n2. Testing GET /stores/{store.id}/inventory/")
        response = client.get(f'/stores/{store.id}/inventory/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', []))
            print(f"   Inventory items: {count}")

        # Test 3: Create order
        print(f"\n3. Testing POST /orders/")
        product = Product.objects.filter(inventory__store=store).first()
        if product:
            inventory = Inventory.objects.get(store=store, product=product)
            order_data = {
                'store_id': store.id,
                'items': [
                    {
                        'product_id': product.id,
                        'quantity_requested': min(2, inventory.quantity)
                    }
                ]
            }
            response = client.post(
                '/orders/',
                data=json.dumps(order_data),
                content_type='application/json'
            )
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"   Order created successfully")
                data = response.json()
                print(f"   Order status: {data.get('status')}")
            else:
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")

        # Test 4: List orders for store
        print(f"\n4. Testing GET /stores/{store.id}/orders/")
        response = client.get(f'/stores/{store.id}/orders/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Orders found: {len(data.get('results', []))}")

    # Test 5: Product search
    print("\n5. Testing GET /api/search/products/?q=test")
    response = client.get('/api/search/products/?q=test')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Products found: {len(data.get('results', []))}")

    # Test 6: Autocomplete
    print("\n6. Testing GET /api/search/suggest/?q=pro")
    response = client.get('/api/search/suggest/?q=pro')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        suggestions = data.get('suggestions', [])
        print(f"   Suggestions: {len(suggestions)}")
        if suggestions:
            print(f"   First suggestion: {suggestions[0]}")

    print("\n" + "=" * 60)
    print("API TESTS COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_endpoints()
