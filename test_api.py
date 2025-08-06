#!/usr/bin/env python3
"""
Test script for the Dynamic API Microservice
This script demonstrates how to create and use dynamic APIs via HTTP requests.
"""

import requests
import json
import time
from examples.schemas import EXAMPLE_REQUESTS

# Configuration
BASE_URL = "http://localhost:8000"
MANAGEMENT_API = f"{BASE_URL}/manage/apis"


def test_api_creation():
    """Test creating dynamic APIs using JSON schemas."""
    print("🚀 Testing Dynamic API Creation")
    print("=" * 50)
    
    for example in EXAMPLE_REQUESTS[:2]:  # Test first 2 examples
        print(f"\n📝 Creating API: {example['name']}")
        
        response = requests.post(MANAGEMENT_API, json=example)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['message']}")
            print(f"   Prefix: {result['data']['prefix']}")
            print(f"   Endpoints: {len(result['data']['endpoints'])} endpoints created")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")


def test_list_apis():
    """Test listing all created APIs."""
    print("\n📋 Listing all APIs")
    print("=" * 30)
    
    response = requests.get(MANAGEMENT_API)
    
    if response.status_code == 200:
        result = response.json()
        apis = result['data']['apis']
        print(f"✅ Found {len(apis)} APIs:")
        
        for api in apis:
            print(f"   • {api['name']} - {api['prefix']}")
            print(f"     Created: {api['created_at']}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")


def test_dynamic_crud_operations():
    """Test CRUD operations on dynamically created APIs."""
    print("\n🔧 Testing CRUD Operations")
    print("=" * 35)
    
    # Test with products API
    api_name = "products"
    api_url = f"{BASE_URL}/{api_name}"
    
    # Test CREATE
    print(f"\n➕ Creating a product...")
    product_data = {
        "name": "Test Product",
        "price": 29.99,
        "description": "A test product for demonstration",
        "category": "Electronics",
        "in_stock": True,
        "tags": ["test", "demo"],
        "metadata": {"color": "blue", "weight": "1.5kg"}
    }
    
    response = requests.post(api_url, json=product_data)
    if response.status_code in [200, 201]:
        created_product = response.json()
        product_id = created_product.get('id')
        print(f"✅ Product created with ID: {product_id}")
    else:
        print(f"❌ Failed to create product: {response.status_code} - {response.text}")
        return
    
    # Test GET ALL
    print(f"\n📋 Getting all products...")
    response = requests.get(api_url)
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Retrieved {len(products)} products")
    else:
        print(f"❌ Failed to get products: {response.status_code} - {response.text}")
    
    # Test GET ONE
    if product_id:
        print(f"\n🔍 Getting product by ID: {product_id}")
        response = requests.get(f"{api_url}/{product_id}")
        if response.status_code == 200:
            product = response.json()
            print(f"✅ Retrieved product: {product.get('name', 'Unknown')}")
        else:
            print(f"❌ Failed to get product: {response.status_code} - {response.text}")
        
        # Test UPDATE
        print(f"\n✏️  Updating product...")
        update_data = {
            "name": "Updated Test Product",
            "price": 39.99,
            "description": "An updated test product",
            "category": "Electronics",
            "in_stock": False
        }
        
        response = requests.put(f"{api_url}/{product_id}", json=update_data)
        if response.status_code == 200:
            updated_product = response.json()
            print(f"✅ Product updated: {updated_product.get('name', 'Unknown')}")
        else:
            print(f"❌ Failed to update product: {response.status_code} - {response.text}")


def test_schema_validation():
    """Test schema validation endpoint."""
    print("\n🔍 Testing Schema Validation")
    print("=" * 35)
    
    # Test valid schema
    valid_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "count": {"type": "integer"}
        },
        "required": ["title"]
    }
    
    response = requests.post(f"{BASE_URL}/manage/validate-schema", json=valid_schema)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Valid schema test: {result['message']}")
    else:
        print(f"❌ Valid schema test failed: {response.status_code}")
    
    # Test invalid schema
    invalid_schema = {
        "type": "object",
        "invalid_field": "this should not be here"
    }
    
    response = requests.post(f"{BASE_URL}/manage/validate-schema", json=invalid_schema)
    if response.status_code == 200:
        result = response.json()
        if not result['data']['valid']:
            print(f"✅ Invalid schema correctly rejected: {result['message']}")
        else:
            print(f"❌ Invalid schema was accepted incorrectly")


def main():
    """Run all tests."""
    print("🧪 Dynamic API Microservice Test Suite")
    print("=" * 60)
    
    # Check if service is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Service is running and healthy")
        else:
            print("❌ Service health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service. Make sure it's running on http://localhost:8000")
        return
    
    # Run tests
    test_schema_validation()
    test_api_creation()
    time.sleep(1)  # Brief pause
    test_list_apis()
    time.sleep(1)  # Brief pause
    test_dynamic_crud_operations()
    
    print("\n🎉 Test suite completed!")
    print("\n💡 You can now:")
    print("   • Visit http://localhost:8000/docs to see the interactive API documentation")
    print("   • Use the dynamically created endpoints like /products, /users, etc.")
    print("   • Create more APIs by POSTing JSON schemas to /manage/apis")


if __name__ == "__main__":
    main()