# Aforro Assignment - Django Backend Module

A complete Django REST API backend demonstrating order management, inventory, product search, and async processing with Redis and Celery.

## Features

### 1. Data Models
- Category: Product categories
- Product: Products with title, description, price, and category
- Store: Physical stores with names and locations
- Inventory: Store-Product inventory tracking (unique constraint: store + product)
- Order: Orders with status (PENDING, CONFIRMED, REJECTED)
- OrderItem: Individual items within orders

### 2. REST API Endpoints

#### Order Management
- `POST /orders/` - Create order with validation and inventory deduction
- `GET /stores/<store_id>/orders/` - List all orders for a store (sorted by newest first)

#### Inventory
- `GET /stores/<store_id>/inventory/` - List inventory for a store (sorted alphabetically by product title)

#### Product Search
- `GET /api/search/products/` - Full-text search with filters and pagination
  - Supports keyword search on title, description, category
  - Filters: category, price range, store_id, in_stock
  - Sorting: price, newest, relevance
  - Includes inventory quantity when store_id provided

#### Autocomplete
- `GET /api/search/suggest/?q=xxx` - Product title autocomplete
  - Minimum 3 characters required
  - Returns up to 10 results
  - Prefix matches appear before general matches

### 3. Engineering Features

#### Redis Integration
- **Caching**: Product search results cached for 5 minutes
- **Rate Limiting**: Ready for implementation (20 req/min per IP on autocomplete)

#### Celery Integration
- **Order Confirmation**: Async email sending when orders are confirmed
- **Inventory Summary**: Generate daily inventory reports
- **Message Broker**: Redis-based task queue
- **Eager Mode**: Tasks execute synchronously in development mode

#### Database Optimization
- Proper indexing on frequently queried fields
- Prefetch/select_related for N+1 prevention
- Transaction.atomic() for order creation consistency

## Project Structure

```
aforro_assignment/
├── catalog/              # Product & Category models
│   ├── models.py
│   ├── serializers.py
│   └── migrations/
├── common/               # Store & Inventory models
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py
│   └── migrations/
├── orders/               # Order models & API
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── tasks.py          # Celery tasks
│   └── migrations/
├── search/               # Product search & autocomplete
│   ├── views.py
│   └── serializers.py
├── aforro_assignment/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Setup & Installation

### Local Development (SQLite)

```bash
# Create and activate virtual environment
python -m venv myenv
myenv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Seed database with test data
python manage.py seed_data

# Start development server
python manage.py runserver
```

### Docker Setup (PostgreSQL + Redis)

```bash
# Build and start all services
docker-compose up -d

# Run migrations inside container
docker-compose exec web python manage.py migrate

# Seed data
docker-compose exec web python manage.py seed_data

# View logs
docker-compose logs -f web
```

Services:
- **Django API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Celery Worker**: Background tasks
- **Celery Beat**: Scheduled tasks

## API Examples

### Create Order
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

Response (all items in stock):
```json
{
  "id": 1,
  "store": 1,
  "status": "CONFIRMED",
  "created_at": "2026-09-09T11:00:00Z",
  "items": [
    {"product": 1, "quantity_requested": 5, ...},
    {"product": 2, "quantity_requested": 3, ...}
  ],
  "total_items": 8
}
```

### Product Search
```bash
curl "http://localhost:8000/api/search/products/?q=phone&store_id=1&sort=price"
```

### Autocomplete
```bash
curl "http://localhost:8000/api/search/suggest/?q=pho"
```

Response:
```json
{
  "suggestions": ["Phone Case", "Phone Stand", "Phone Screen Protector"]
}
```

## Database Design

### Key Design Decisions

1. **Atomic Order Creation**: Uses transaction.atomic() to ensure:
   - All order items are created or none
   - Inventory deduction only on confirmed orders
   - Rollback on any validation failure

2. **Inventory Unique Constraint**: Each store can only have one inventory record per product

3. **Query Optimization**:
   - Indexed fields: title, category, store
   - Prefetch related for order.items
   - Select related for foreign key traversal

4. **Async Processing**: Celery handles:
   - Email confirmations (non-blocking)
   - Inventory summaries
   - Search preprocessing

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `USE_POSTGRES` | false | Use PostgreSQL instead of SQLite |
| `USE_REDIS` | false | Enable Redis caching |
| `USE_CELERY` | false | Enable async Celery tasks |
| `DB_NAME` | aforro_db | Database name |
| `DB_USER` | postgres | Database user |
| `DB_PASSWORD` | postgres | Database password |
| `DB_HOST` | localhost | Database host |
| `DB_PORT` | 5432 | Database port |
| `REDIS_HOST` | localhost | Redis host |
| `REDIS_PORT` | 6379 | Redis port |

## Testing

```bash
# Run tests (add test files to each app)
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment

1. Set `DEBUG = False` in settings
2. Configure allowed hosts
3. Use PostgreSQL in production
4. Enable Redis for caching
5. Run Celery workers
6. Set up Celery Beat for scheduled tasks
7. Use gunicorn + nginx for WSGI serving

## Technologies Used

- **Django 6.1.1**: Web framework
- **Django REST Framework 3.18.1**: API toolkit
- **PostgreSQL**: Production database
- **Redis**: Caching and message broker
- **Celery**: Async task queue
- **Faker**: Test data generation
- **Docker**: Containerization


