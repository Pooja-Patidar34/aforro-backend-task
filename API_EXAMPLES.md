# API Examples & Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required. Production deployment should add token-based auth.

---

## 1. Order Management

### Create Order
**Endpoint**: `POST /orders/`

**Request**:
```bash
curl -X POST http://localhost:8000/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": 1,
    "items": [
      {"product_id": 1, "quantity_requested": 5},
      {"product_id": 2, "quantity_requested": 3}
    ]
  }'
```

**Response (All items in stock)** - 201 Created:
```json
{
  "id": 1,
  "store": 1,
  "status": "CONFIRMED",
  "created_at": "2026-09-09T11:23:45.123456Z",
  "items": [
    {
      "id": 1,
      "product": 1,
      "product_title": "Electronics Phone",
      "product_price": "599.99",
      "quantity_requested": 5
    },
    {
      "id": 2,
      "product": 2,
      "product_title": "Clothing Shirt",
      "product_price": "49.99",
      "quantity_requested": 3
    }
  ],
  "total_items": 8
}
```

**Response (Insufficient stock)** - 201 Created:
```json
{
  "id": 2,
  "store": 1,
  "status": "REJECTED",
  "created_at": "2026-09-09T11:24:00.123456Z",
  "items": [
    {
      "id": 3,
      "product": 3,
      "product_title": "Book Novel",
      "product_price": "29.99",
      "quantity_requested": 100
    }
  ],
  "total_items": 100
}
```

**Status Codes**:
- `201 Created`: Order created (check status field)
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Store or product not found

**Business Logic**:
- If ALL products have sufficient stock → status: "CONFIRMED", inventory deducted
- If ANY product has insufficient stock → status: "REJECTED", NO inventory deduction
- Entire operation wrapped in database transaction
- On CONFIRMED orders, async email task is triggered

---

### List Orders for Store
**Endpoint**: `GET /stores/<store_id>/orders/`

**Request**:
```bash
curl http://localhost:8000/stores/1/orders/
```

**Response** - 200 OK:
```json
{
  "count": 15,
  "next": "http://localhost:8000/stores/1/orders/?page=2",
  "previous": null,
  "results": [
    {
      "id": 8,
      "store": 1,
      "status": "CONFIRMED",
      "created_at": "2026-09-09T11:30:00.123456Z",
      "items": [
        {
          "id": 21,
          "product": 5,
          "product_title": "Electronics Laptop",
          "product_price": "1299.99",
          "quantity_requested": 2
        }
      ],
      "total_items": 2
    },
    {
      "id": 7,
      "store": 1,
      "status": "CONFIRMED",
      "created_at": "2026-09-09T11:25:00.123456Z",
      "items": [
        {
          "id": 19,
          "product": 4,
          "product_title": "Food Coffee",
          "product_price": "12.99",
          "quantity_requested": 10
        }
      ],
      "total_items": 10
    }
  ]
}
```

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Features**:
- Sorted by newest first (created_at descending)
- Includes all order items with product details
- Total items count per order
- Pagination support

---

## 2. Inventory Management

### List Store Inventory
**Endpoint**: `GET /stores/<store_id>/inventory/`

**Request**:
```bash
curl http://localhost:8000/stores/1/inventory/
```

**Response** - 200 OK:
```json
{
  "count": 45,
  "next": "http://localhost:8000/stores/1/inventory/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "product": 1,
      "product_title": "Apple Orange",
      "product_price": "2.99",
      "category_name": "Food & Beverages",
      "quantity": 125
    },
    {
      "id": 2,
      "product": 2,
      "product_title": "Banana Fruit",
      "product_price": "1.50",
      "category_name": "Food & Beverages",
      "quantity": 87
    },
    {
      "id": 3,
      "product": 3,
      "product_title": "Book Novel",
      "product_price": "19.99",
      "category_name": "Books",
      "quantity": 34
    }
  ]
}
```

**Features**:
- Sorted alphabetically by product title
- Includes product price and category
- Shows current quantity on hand
- Pagination support (20 items per page)

**Query Parameters**:
- `page`: Page number
- `page_size`: Items per page

---

## 3. Product Search

### Search Products
**Endpoint**: `GET /api/search/products/`

**Basic Search**:
```bash
curl 'http://localhost:8000/api/search/products/?q=phone'
```

**Search with Filters**:
```bash
curl 'http://localhost:8000/api/search/products/?q=electronics&category=1&price_min=100&price_max=500&sort=price'
```

**Search with Store Inventory**:
```bash
curl 'http://localhost:8000/api/search/products/?q=laptop&store_id=1&in_stock=true'
```

**Response** - 200 OK:
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/search/products/?q=phone&page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "iPhone 15 Pro",
      "description": "Latest Apple smartphone with advanced camera",
      "price": "999.99",
      "category_name": "Electronics",
      "inventory_quantity": 5
    },
    {
      "id": 2,
      "title": "Samsung Phone",
      "description": "High-end Android phone",
      "price": "899.99",
      "category_name": "Electronics",
      "inventory_quantity": 12
    },
    {
      "id": 3,
      "title": "Phone Case Premium",
      "description": "Protective case for phones",
      "price": "29.99",
      "category_name": "Accessories",
      "inventory_quantity": 0
    }
  ]
}
```

### Query Parameters

**Search**:
- `q`: Keyword search (searches title, description, category)

**Filters**:
- `category`: Category ID
- `price_min`: Minimum price
- `price_max`: Maximum price
- `store_id`: Filter by store (includes inventory)
- `in_stock`: Set to "true" to show only in-stock items for a store

**Sorting**:
- `sort=price`: Sort by price (ascending)
- `sort=newest`: Sort by created date (newest first)
- `sort=relevance`: Keyword relevance (prefix matches first)

**Pagination**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

### Search Examples

**Electronics under $500**:
```bash
curl 'http://localhost:8000/api/search/products/?q=electronics&price_max=500&sort=price'
```

**In-stock items at store #1**:
```bash
curl 'http://localhost:8000/api/search/products/?store_id=1&in_stock=true&sort=newest'
```

**All books sorted by relevance**:
```bash
curl 'http://localhost:8000/api/search/products/?q=book&sort=relevance&page_size=50'
```

---

## 4. Autocomplete

### Get Product Suggestions
**Endpoint**: `GET /api/search/suggest/`

**Request**:
```bash
curl 'http://localhost:8000/api/search/suggest/?q=pho'
```

**Response** - 200 OK:
```json
{
  "suggestions": [
    "Phone Case",
    "Phone Stand",
    "Phone Screen Protector",
    "Smartphone",
    "Photography Book",
    "Telephone Cord",
    "Household Phone",
    "Professional Phone Mount",
    "Cellular Phone",
    "Wireless Phone"
  ]
}
```

### Requirements
- Minimum 3 characters required in query
- Returns up to 10 suggestions
- Prefix matches appear first (results starting with query)
- Then general matches (results containing query anywhere)

### Query Parameters
- `q`: Search query (minimum 3 characters)

### Examples

**Query too short** (< 3 chars):
```bash
curl 'http://localhost:8000/api/search/suggest/?q=ph'
```
Returns: `{"suggestions": []}`

**Prefix match example**:
```bash
curl 'http://localhost:8000/api/search/suggest/?q=ele'
```
Returns: Products starting with "ele" first (Electronics, Electric, etc.)

---

## 5. Store Management

### List All Stores
**Endpoint**: `GET /api/stores/`

**Request**:
```bash
curl http://localhost:8000/api/stores/
```

**Response** - 200 OK:
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Downtown Electronics",
      "location": "123 Main St, New York, NY"
    },
    {
      "id": 2,
      "name": "Shopping Mall Store",
      "location": "456 Plaza Dr, Los Angeles, CA"
    },
    {
      "id": 3,
      "name": "Suburban Outlet",
      "location": "789 Park Ave, Chicago, IL"
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request - Invalid Order
```json
{
  "error": "Product with id 999 not found"
}
```

### 404 Not Found - Store Not Found
```json
{
  "detail": "Not found."
}
```

### 400 Bad Request - Empty Items List
```json
{
  "items": ["At least one item is required."]
}
```

---

## Headers & Content Types

**All requests** should include:
```
Content-Type: application/json
```

**Response headers**:
```
Content-Type: application/json
```

---

## Rate Limiting

Currently not implemented. When enabled:
- Autocomplete endpoint: 20 requests per minute per IP
- Other endpoints: 100 requests per minute

---

## Pagination

All list endpoints support pagination:

**Default**: 20 items per page

**Custom page size**:
```bash
curl 'http://localhost:8000/api/stores/?page_size=50'
```

**Navigate pages**:
```bash
curl 'http://localhost:8000/api/stores/?page=2'
```

Response includes:
- `count`: Total number of items
- `next`: URL for next page (null if last page)
- `previous`: URL for previous page (null if first page)
- `results`: Array of items

---

## Performance Tips

1. **Use store_id with search**: Reduces data transferred
2. **Specify page_size**: Adjust based on client capacity
3. **Use in_stock filter**: Avoids out-of-stock items
4. **Sort by price**: Customers often filter by budget
5. **Autocomplete caching**: Results cached client-side for 30 seconds

---

## Testing

Run the included test suite:
```bash
python test_api.py
```

All endpoints are tested and return expected status codes and data.
