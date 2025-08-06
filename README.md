# Dynamic API Microservice

A powerful Python-based microservice built with FastAPI that dynamically generates CRUD APIs based on JSON schemas. This service leverages the FastAPI CRUD Router library to automatically create database tables, Pydantic models, and REST endpoints from JSON schema definitions posted via API.

## 🚀 Features

- **Dynamic API Generation**: Create full CRUD APIs by simply posting a JSON schema
- **PostgreSQL Support**: Built-in support for PostgreSQL with async operations
- **FastAPI CRUD Router**: Leverages the powerful fastapi-crudrouter library
- **Automatic Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Schema Validation**: Built-in JSON schema validation
- **Flexible Configuration**: Customizable pagination, route enabling/disabling
- **Docker Support**: Complete Docker and Docker Compose setup
- **Production Ready**: Proper error handling, logging, and health checks

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Option 1: Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd dynamic-api-microservice
```

2. Start the services:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- The API service on port 8000

### Option 2: Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL and create a database:
```sql
CREATE DATABASE dynamic_api_db;
CREATE USER user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE dynamic_api_db TO user;
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📖 Usage

### 1. Access the API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Create a Dynamic API

Send a POST request to `/manage/apis` with a JSON schema:

```bash
curl -X POST "http://localhost:8000/manage/apis" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "products",
       "schema": {
         "type": "object",
         "properties": {
           "name": {"type": "string", "description": "Product name"},
           "price": {"type": "number", "description": "Product price"},
           "category": {"type": "string", "description": "Product category"},
           "in_stock": {"type": "boolean", "default": true}
         },
         "required": ["name", "price", "category"]
       },
       "options": {
         "pagination": {"enabled": true, "size": 10},
         "routes": {
           "get_all": true,
           "get_one": true,
           "create": true,
           "update": true,
           "delete_one": true,
           "delete_all": false
         }
       }
     }'
```

This creates a complete CRUD API at `/products` with the following endpoints:
- `GET /products` - List all products (with pagination)
- `POST /products` - Create a new product
- `GET /products/{id}` - Get a specific product
- `PUT /products/{id}` - Update a product
- `DELETE /products/{id}` - Delete a product

### 3. Use the Generated API

Once created, you can immediately use the new API:

```bash
# Create a product
curl -X POST "http://localhost:8000/products" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Laptop",
       "price": 999.99,
       "category": "Electronics",
       "in_stock": true
     }'

# List all products
curl "http://localhost:8000/products"

# Get a specific product
curl "http://localhost:8000/products/1"

# Update a product
curl -X PUT "http://localhost:8000/products/1" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Gaming Laptop",
       "price": 1299.99,
       "category": "Electronics",
       "in_stock": true
     }'
```

### 4. Management Operations

```bash
# List all created APIs
curl "http://localhost:8000/manage/apis"

# Get info about a specific API
curl "http://localhost:8000/manage/apis/products"

# Delete an API
curl -X DELETE "http://localhost:8000/manage/apis/products"

# Validate a schema before creating
curl -X POST "http://localhost:8000/manage/validate-schema" \
     -H "Content-Type: application/json" \
     -d '{
       "type": "object",
       "properties": {
         "title": {"type": "string"}
       }
     }'
```

## 🧪 Testing

Run the included test suite:

```bash
python test_api.py
```

Or run the comprehensive usage examples:

```bash
python examples/api_usage.py
```

This will:
1. Validate the service is running
2. Test schema validation
3. Create sample APIs (products, users)
4. Test CRUD operations
5. List created APIs

## 🔧 Troubleshooting

### Pydantic v2 Compatibility
The service is fully compatible with Pydantic v2. If you encounter `'FieldInfo' object has no attribute 'type_'` errors, make sure you're using the latest version with the fixes included.

### Common Issues
- **Database Connection**: Ensure PostgreSQL is running and accessible
- **Port Conflicts**: Change ports in docker-compose.yml if 8000 or 5432 are in use
- **Memory Issues**: Increase Docker memory if creating many large APIs

## 📊 JSON Schema Support

The service supports comprehensive JSON schema definitions:

### Supported Types
- `string` - Text fields (with maxLength, format support)
- `integer` - Whole numbers (with min/max validation)
- `number` - Decimal numbers (with min/max validation)
- `boolean` - True/false values
- `array` - Lists of items
- `object` - Nested objects/JSON

### Special Formats
- `datetime` - Automatically handled as timestamp fields
- `email` - String validation for email addresses
- `uuid` - String fields for UUID values

### Example Schema
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "The title",
      "maxLength": 100
    },
    "count": {
      "type": "integer",
      "description": "Count value",
      "minimum": 0,
      "maximum": 1000
    },
    "price": {
      "type": "number",
      "description": "Price in USD",
      "minimum": 0
    },
    "active": {
      "type": "boolean",
      "description": "Is active",
      "default": true
    },
    "tags": {
      "type": "array",
      "description": "List of tags",
      "items": {"type": "string"}
    },
    "metadata": {
      "type": "object",
      "description": "Additional data"
    },
    "created_at": {
      "type": "string",
      "format": "datetime",
      "description": "Creation timestamp"
    }
  },
  "required": ["title", "count"]
}
```

## ⚙️ Configuration Options

When creating APIs, you can specify options:

```json
{
  "pagination": {
    "enabled": true,
    "size": 20
  },
  "routes": {
    "get_all": true,
    "get_one": true,
    "create": true,
    "update": true,
    "delete_one": true,
    "delete_all": false
  }
}
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│  Management API          │  Dynamic CRUD APIs              │
│  /manage/apis            │  /products, /users, /events...   │
├─────────────────────────────────────────────────────────────┤
│              FastAPI CRUD Router Library                    │
├─────────────────────────────────────────────────────────────┤
│  Dynamic Model Generator │  API Registry                   │
│  JSON Schema → Pydantic  │  Track Created APIs             │
├─────────────────────────────────────────────────────────────┤
│              Databases (Async PostgreSQL)                   │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dynamic_api_db

# Application Settings
APP_NAME="Dynamic API Microservice"
DEBUG=true

# API Settings
DOCS_URL="/docs"
REDOC_URL="/redoc"

# Dynamic API Settings
MAX_DYNAMIC_APIS=50
DEFAULT_PAGINATION_SIZE=20
```

## 🚦 Health Check

Check service health:
```bash
curl "http://localhost:8000/health"
```

## 📝 Example Use Cases

1. **Rapid Prototyping**: Quickly create APIs for frontend development
2. **Content Management**: Dynamic content types without code changes
3. **Data Collection**: Forms and surveys with custom fields
4. **Microservices**: Generate service-specific APIs on demand
5. **Testing**: Create test APIs with specific schemas

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the example schemas in `examples/schemas.py`
3. Run the test suite with `python test_api.py`
4. Open an issue on GitHub

---

**Built with ❤️ using FastAPI and FastAPI CRUD Router**