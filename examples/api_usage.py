#!/usr/bin/env python3
"""
Example usage of the Dynamic API Microservice
This shows how to create and use dynamic APIs via HTTP requests.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
MANAGEMENT_API = f"{BASE_URL}/manage/apis"

def create_product_api():
    """Create a products API with the fixed schema format."""
    
    # Product API schema - compatible with Pydantic v2
    product_request = {
        "name": "products",
        "schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Product name",
                    "maxLength": 100
                },
                "price": {
                    "type": "number",
                    "description": "Product price in USD",
                    "minimum": 0
                },
                "description": {
                    "type": "string", 
                    "description": "Product description"
                },
                "category": {
                    "type": "string",
                    "description": "Product category"
                },
                "in_stock": {
                    "type": "boolean",
                    "description": "Whether the product is in stock",
                    "default": True
                },
                "tags": {
                    "type": "array",
                    "description": "Product tags",
                    "items": {
                        "type": "string"
                    }
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional product metadata"
                }
            },
            "required": ["name", "price", "category"]
        },
        "options": {
            "pagination": {"enabled": True, "size": 10},
            "routes": {
                "get_all": True,
                "get_one": True,
                "create": True,
                "update": True,
                "delete_one": True,
                "delete_all": False
            }
        }
    }
    
    print("🛍️  Creating Products API...")
    response = requests.post(MANAGEMENT_API, json=product_request)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success: {result['message']}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def create_user_api():
    """Create a users API."""
    
    user_request = {
        "name": "users",
        "schema": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Unique username"
                },
                "email": {
                    "type": "string",
                    "description": "User email address"
                },
                "first_name": {
                    "type": "string",
                    "description": "User's first name"
                },
                "last_name": {
                    "type": "string", 
                    "description": "User's last name"
                },
                "age": {
                    "type": "integer",
                    "description": "User's age",
                    "minimum": 0
                },
                "is_active": {
                    "type": "boolean",
                    "description": "Whether the user account is active",
                    "default": True
                }
            },
            "required": ["username", "email"]
        }
    }
    
    print("👥 Creating Users API...")
    response = requests.post(MANAGEMENT_API, json=user_request)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success: {result['message']}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_product_operations():
    """Test CRUD operations on the products API."""
    
    api_url = f"{BASE_URL}/products"
    
    print("\n🧪 Testing Product CRUD Operations")
    print("=" * 40)
    
    # CREATE a product
    print("➕ Creating a product...")
    product_data = {
        "name": "Gaming Laptop",
        "price": 1299.99,
        "description": "High-performance gaming laptop",
        "category": "Electronics",
        "in_stock": True,
        "tags": ["gaming", "laptop", "electronics"],
        "metadata": {
            "brand": "TechBrand",
            "warranty": "2 years",
            "color": "black"
        }
    }
    
    response = requests.post(api_url, json=product_data)
    if response.status_code in [200, 201]:
        created_product = response.json()
        product_id = created_product.get('id')
        print(f"✅ Product created with ID: {product_id}")
        print(f"   Name: {created_product.get('name')}")
    else:
        print(f"❌ Failed to create product: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    # READ all products
    print("\n📋 Getting all products...")
    response = requests.get(api_url)
    if response.status_code == 200:
        products = response.json()
        count = len(products) if isinstance(products, list) else products.get('count', 0)
        print(f"✅ Retrieved {count} products")
    else:
        print(f"❌ Failed to get products: {response.status_code}")
    
    # READ one product
    if product_id:
        print(f"\n🔍 Getting product by ID: {product_id}")
        response = requests.get(f"{api_url}/{product_id}")
        if response.status_code == 200:
            product = response.json()
            print(f"✅ Retrieved product: {product.get('name')}")
            print(f"   Price: ${product.get('price')}")
        else:
            print(f"❌ Failed to get product: {response.status_code}")
        
        # UPDATE the product
        print(f"\n✏️  Updating product...")
        update_data = {
            "name": "Ultra Gaming Laptop",
            "price": 1499.99,
            "description": "Ultra high-performance gaming laptop",
            "category": "Electronics",
            "in_stock": True
        }
        
        response = requests.put(f"{api_url}/{product_id}", json=update_data)
        if response.status_code == 200:
            updated_product = response.json()
            print(f"✅ Product updated: {updated_product.get('name')}")
            print(f"   New price: ${updated_product.get('price')}")
        else:
            print(f"❌ Failed to update product: {response.status_code}")

def test_user_operations():
    """Test CRUD operations on the users API."""
    
    api_url = f"{BASE_URL}/users"
    
    print("\n👤 Testing User CRUD Operations")
    print("=" * 35)
    
    # CREATE a user
    print("➕ Creating a user...")
    user_data = {
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "is_active": True
    }
    
    response = requests.post(api_url, json=user_data)
    if response.status_code in [200, 201]:
        created_user = response.json()
        user_id = created_user.get('id')
        print(f"✅ User created with ID: {user_id}")
        print(f"   Username: {created_user.get('username')}")
    else:
        print(f"❌ Failed to create user: {response.status_code}")
        print(f"   Error: {response.text}")

def main():
    """Main function to run all examples."""
    
    print("🚀 Dynamic API Microservice - Usage Examples")
    print("=" * 60)
    
    # Check service health
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Service is healthy and running")
        else:
            print("❌ Service health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service")
        print("   Make sure the service is running: ./start.sh")
        return
    
    # Create APIs
    print("\n📝 Creating Dynamic APIs")
    print("=" * 30)
    
    success1 = create_product_api()
    time.sleep(1)
    success2 = create_user_api()
    
    if success1:
        time.sleep(2)  # Give time for API to be ready
        test_product_operations()
    
    if success2:
        time.sleep(2)  # Give time for API to be ready
        test_user_operations()
    
    # Show available APIs
    print("\n📋 Available APIs")
    print("=" * 20)
    response = requests.get(MANAGEMENT_API)
    if response.status_code == 200:
        result = response.json()
        apis = result['data']['apis']
        for api in apis:
            print(f"• {api['name']} - {api['prefix']}")
    
    print("\n🎉 Examples completed!")
    print("\n💡 Next steps:")
    print("   • Visit http://localhost:8000/docs to explore the APIs")
    print("   • Try creating your own APIs with different schemas")
    print("   • Use the generated endpoints in your applications")

if __name__ == "__main__":
    main()