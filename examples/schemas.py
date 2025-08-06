"""
Example JSON schemas for creating dynamic APIs
"""

# Example 1: Product Management API
PRODUCT_SCHEMA = {
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
            "description": "Product description",
            "maxLength": 1000
        },
        "category": {
            "type": "string",
            "description": "Product category",
            "maxLength": 50
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
}

# Example 2: User Management API
USER_SCHEMA = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string",
            "description": "Unique username",
            "maxLength": 50
        },
        "email": {
            "type": "string",
            "description": "User email address",
            "format": "email",
            "maxLength": 255
        },
        "first_name": {
            "type": "string",
            "description": "User's first name",
            "maxLength": 50
        },
        "last_name": {
            "type": "string",
            "description": "User's last name",
            "maxLength": 50
        },
        "age": {
            "type": "integer",
            "description": "User's age",
            "minimum": 0,
            "maximum": 150
        },
        "is_active": {
            "type": "boolean",
            "description": "Whether the user account is active",
            "default": True
        },
        "profile": {
            "type": "object",
            "description": "User profile information"
        }
    },
    "required": ["username", "email"]
}

# Example 3: Blog Post API
BLOG_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Blog post title",
            "maxLength": 200
        },
        "content": {
            "type": "string",
            "description": "Blog post content (HTML allowed)"
        },
        "author": {
            "type": "string",
            "description": "Author name",
            "maxLength": 100
        },
        "published": {
            "type": "boolean",
            "description": "Whether the post is published",
            "default": False
        },
        "created_at": {
            "type": "string",
            "format": "datetime",
            "description": "Creation timestamp"
        },
        "updated_at": {
            "type": "string",
            "format": "datetime",
            "description": "Last update timestamp"
        },
        "tags": {
            "type": "array",
            "description": "Post tags",
            "items": {
                "type": "string"
            }
        },
        "view_count": {
            "type": "integer",
            "description": "Number of views",
            "default": 0,
            "minimum": 0
        }
    },
    "required": ["title", "content", "author"]
}

# Example 4: Event Management API
EVENT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Event name",
            "maxLength": 150
        },
        "description": {
            "type": "string",
            "description": "Event description"
        },
        "start_date": {
            "type": "string",
            "format": "datetime",
            "description": "Event start date and time"
        },
        "end_date": {
            "type": "string",
            "format": "datetime",
            "description": "Event end date and time"
        },
        "location": {
            "type": "string",
            "description": "Event location",
            "maxLength": 200
        },
        "capacity": {
            "type": "integer",
            "description": "Maximum number of attendees",
            "minimum": 1
        },
        "price": {
            "type": "number",
            "description": "Ticket price",
            "minimum": 0,
            "default": 0
        },
        "is_public": {
            "type": "boolean",
            "description": "Whether the event is public",
            "default": True
        },
        "organizer": {
            "type": "object",
            "description": "Event organizer information"
        }
    },
    "required": ["name", "start_date", "end_date", "location"]
}

# Example API creation requests
EXAMPLE_REQUESTS = [
    {
        "name": "products",
        "schema": PRODUCT_SCHEMA,
        "options": {
            "pagination": {"enabled": True, "size": 10},
            "routes": {
                "get_all": True,
                "get_one": True,
                "create": True,
                "update": True,
                "delete_one": True,
                "delete_all": False  # Disable bulk delete for safety
            }
        }
    },
    {
        "name": "users",
        "schema": USER_SCHEMA,
        "options": {
            "pagination": {"enabled": True, "size": 20},
            "routes": {
                "get_all": True,
                "get_one": True,
                "create": True,
                "update": True,
                "delete_one": True,
                "delete_all": False
            }
        }
    },
    {
        "name": "posts",
        "schema": BLOG_POST_SCHEMA,
        "options": {
            "pagination": {"enabled": True, "size": 15},
            "routes": {
                "get_all": True,
                "get_one": True,
                "create": True,
                "update": True,
                "delete_one": True,
                "delete_all": False
            }
        }
    },
    {
        "name": "events",
        "schema": EVENT_SCHEMA,
        "options": {
            "pagination": {"enabled": True, "size": 25},
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
]