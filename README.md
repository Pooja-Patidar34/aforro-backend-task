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

## 📚 API Documentation & Testing

### Swagger UI (Interactive API Explorer)
- **URL**: http://localhost:8000/api/docs/
- **Features**: Test all endpoints directly from the browser
- **Auto-generated**: From DRF serializers and viewsets

### ReDoc (Alternative Documentation)
- **URL**: http://localhost:8000/api/redoc/
- **Features**: Clean, readable API documentation

### OpenAPI Schema
- **URL**: http://localhost:8000/api/schema/
- **Format**: JSON OpenAPI 3.0 schema

### Postman Collection
- **File**: `Postman_Collection.json` (included in repo)
- **Import**: Open Postman → Import → Select file
- **Ready to Use**: All 6 endpoints with sample requests

## Project Structure

```
aforro_assignment/
├── products/             # Product & Category models
│   ├── models.py
│   ├── serializers.py
│   └── migrations/
├── stores/               # Store & Inventory models
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
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── API_EXAMPLES.md
```

## Setup & Installation

### Option 1: Local Development (SQLite) - Recommended for Quick Start

#### Step 1: Clone Repository
```bash
git clone https://github.com/Pooja-Patidar34/aforro-backend-task.git
cd aforro-backend-task
```

#### Step 2: Create & Activate Virtual Environment
```powershell
# Windows (PowerShell)
python -m venv myenv
.\myenv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv myenv
myenv\Scripts\activate.bat

# Linux/Mac
python -m venv myenv
source myenv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run Database Migrations
```bash
python manage.py migrate
```

#### Step 5: Seed Database with Test Data
```bash
python manage.py seed_data
```
This creates:
- 12+ categories
- 1000+ products
- 20+ stores
- 6000+ inventory records

#### Step 6: Start Development Server
```bash
python manage.py runserver
```

**Server running at**: http://localhost:8000

#### Step 7: Test the API
```bash
# In a new terminal (with venv activated)
python test_api.py
```

You should see all 6 endpoints working! ✅

### Option 2: Docker Setup (PostgreSQL + Redis) - Production-like

#### Step 1: Clone Repository
```bash
git clone https://github.com/Pooja-Patidar34/aforro-backend-task.git
cd aforro-backend-task
```

#### Step 2: Build and Start All Services
```bash
docker-compose up -d
```

This starts 5 services:
- Django API (port 8000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Celery Worker (background)
- Celery Beat (scheduler)

#### Step 3: Run Database Migrations
```bash
docker-compose exec web python manage.py migrate
```

#### Step 4: Seed Database
```bash
docker-compose exec web python manage.py seed_data
```

#### Step 5: Access Services
- **Django API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

#### Step 6: View Logs
```bash
docker-compose logs -f web
```

#### Step 7: Stop Services
```bash
docker-compose down
```

## Quick API Test

After setup, test the API immediately:

```bash
# Option 1: Run automated test
python test_api.py

# Option 2: Test individual endpoints
curl http://localhost:8000/api/stores/
curl http://localhost:8000/api/search/products/?q=test
curl http://localhost:8000/api/search/suggest/?q=pro

# Option 3: View interactive docs
# Open http://localhost:8000/api/docs/ in browser
```

Expected results: All 6 endpoints return 200 OK ✅

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

### Automated API Tests
```bash
# Test all 6 API endpoints
python test_api.py
```

Expected output:
```
✅ GET /api/stores/              → 200 OK (20 stores)
✅ GET /stores/{id}/inventory/   → 200 OK (20 items)
✅ POST /orders/                 → 201 CREATED
✅ GET /stores/{id}/orders/      → 200 OK
✅ GET /api/search/products/     → 200 OK
✅ GET /api/search/suggest/      → 200 OK
```

### Django Test Suite
```bash
# Run all tests
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

## Troubleshooting

### Port 8000 Already in Use
```bash
# Find and kill the process
# Windows: Use Task Manager or
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000
kill -9 <PID>

# Or run on different port
python manage.py runserver 8080
```

### Database Locked (SQLite)
```bash
# Delete database and restart
del db.sqlite3
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

### Virtual Environment Issues
```bash
# Deactivate and reactivate
deactivate
.\myenv\Scripts\Activate.ps1

# Or reinstall packages
pip install -r requirements.txt --force-reinstall
```

### Docker Issues
```bash
# Stop and remove containers
docker-compose down

# Rebuild images
docker-compose up -d --build

# View logs for errors
docker-compose logs web
```

## Notes

- **Caching**: Product search results cached for 5 minutes in Redis
- **Async Tasks**: Order confirmations sent asynchronously via Celery
- **Database**: Uses SQLite locally, PostgreSQL in Docker
- **Performance**: Optimized queries with indexes and select_related/prefetch_related
- **Scalability**: Ready for horizontal scaling with separate workers, caching, and async tasks

## Technologies Used

- **Django 6.1.1**: Web framework
- **Django REST Framework 3.18.1**: API toolkit
- **PostgreSQL**: Production database
- **Redis**: Caching and message broker
- **Celery**: Async task queue
- **Faker**: Test data generation
- **Docker**: Containerization


