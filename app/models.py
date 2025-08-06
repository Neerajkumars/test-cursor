from pydantic import BaseModel, create_model, Field
from typing import Dict, Any, Type, Optional, Union, List, get_origin, get_args
import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
import sys

Base = declarative_base()


class DynamicModelGenerator:
    """Generator for creating dynamic Pydantic models and SQLAlchemy tables from JSON schema."""
    
    # Type mapping from JSON schema types to Python types
    TYPE_MAPPING = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    
    # Type mapping for SQLAlchemy columns
    SQLALCHEMY_TYPE_MAPPING = {
        "string": String,
        "integer": Integer,
        "number": Float,
        "boolean": Boolean,
        "array": JSON,
        "object": JSON,
        "datetime": DateTime,
        "text": Text,
    }
    
    @classmethod
    def create_pydantic_model(
        cls, 
        name: str, 
        schema: Dict[str, Any], 
        base_class: Type[BaseModel] = BaseModel
    ) -> Type[BaseModel]:
        """Create a Pydantic model from JSON schema."""
        
        if "properties" not in schema:
            raise ValueError("Schema must contain 'properties' field")
        
        properties = schema["properties"]
        required_fields = schema.get("required", [])
        
        # Build field definitions
        fields = {}
        
        for field_name, field_schema in properties.items():
            base_type = cls._get_pydantic_type(field_schema)
            default_value = cls._get_default_value(field_schema, field_name in required_fields)
            is_required = field_name in required_fields
            
            # Handle type optionality based on whether field is required
            if is_required and default_value is ...:
                # Required field without default
                field_type = base_type
                fields[field_name] = (field_type, Field(..., description=field_schema.get("description", "")))
            else:
                # Optional field or field with default
                from typing import Union
                if (hasattr(base_type, '__origin__') and base_type.__origin__ is Union) or \
                   (sys.version_info >= (3, 8) and get_origin(base_type) is Union):
                    # Already Optional/Union
                    field_type = base_type
                else:
                    # Make it Optional
                    field_type = Union[base_type, None]
                
                if default_value is ...:
                    fields[field_name] = (field_type, Field(None, description=field_schema.get("description", "")))
                else:
                    fields[field_name] = (field_type, Field(default=default_value, description=field_schema.get("description", "")))
        
        # Add id field if not present
        if "id" not in fields:
            from typing import Union
            fields["id"] = (Union[int, None], Field(None, description="Unique identifier"))
        
        # Create the model
        return create_model(name, **fields, __base__=base_class)
    
    @classmethod
    def create_create_model(cls, base_model: Type[BaseModel], name: str) -> Type[BaseModel]:
        """Create a 'Create' version of the model (without id field)."""
        fields = {}
        
        for field_name, field_info in base_model.model_fields.items():
            if field_name != "id":  # Exclude id field for create operations
                # Pydantic v2 compatibility
                field_type = field_info.annotation
                
                # Handle default values properly for Pydantic v2
                if hasattr(field_info, 'default') and field_info.default is not ...:
                    default_val = field_info.default
                elif hasattr(field_info, 'default_factory') and field_info.default_factory is not None:
                    default_val = Field(default_factory=field_info.default_factory)
                else:
                    default_val = ...
                
                # Get description safely
                description = getattr(field_info, 'description', '') or ''
                
                if default_val is ...:
                    fields[field_name] = (field_type, Field(..., description=description))
                else:
                    fields[field_name] = (field_type, Field(default=default_val, description=description))
        
        return create_model(f"{name}Create", **fields)
    
    @classmethod
    def create_sqlalchemy_table(cls, name: str, schema: Dict[str, Any], metadata) -> sqlalchemy.Table:
        """Create a SQLAlchemy table from JSON schema."""
        
        if "properties" not in schema:
            raise ValueError("Schema must contain 'properties' field")
        
        properties = schema["properties"]
        columns = []
        
        # Add id column if not present
        if "id" not in properties:
            columns.append(Column("id", Integer, primary_key=True, index=True))
        
        for field_name, field_schema in properties.items():
            if field_name == "id":
                columns.append(Column("id", Integer, primary_key=True, index=True))
            else:
                column_type = cls._get_sqlalchemy_type(field_schema)
                nullable = field_name not in schema.get("required", [])
                columns.append(Column(field_name, column_type, nullable=nullable))
        
        table_name = f"dynamic_{name.lower()}"
        return sqlalchemy.Table(table_name, metadata, *columns)
    
    @classmethod
    def _get_pydantic_type(cls, field_schema: Dict[str, Any]) -> Type:
        """Get Python type for Pydantic model from field schema."""
        from typing import Union
        
        field_type = field_schema.get("type", "string")
        
        # Handle special formats
        if field_type == "string":
            format_type = field_schema.get("format")
            if format_type == "datetime":
                return Union[datetime, None]
            elif format_type == "uuid":
                return Union[str, None]
        
        # Handle arrays
        if field_type == "array":
            items_schema = field_schema.get("items", {})
            item_type = cls._get_pydantic_type(items_schema)
            # Remove Optional wrapper for item type in arrays
            if (hasattr(item_type, '__origin__') and item_type.__origin__ is Union) or \
               (sys.version_info >= (3, 8) and get_origin(item_type) is Union):
                args = getattr(item_type, '__args__', None) or get_args(item_type)
                if args and len(args) >= 2 and type(None) in args:
                    # Get the non-None type
                    item_type = next(arg for arg in args if arg is not type(None))
            return Union[List[item_type], None]
        
        # Get base type
        python_type = cls.TYPE_MAPPING.get(field_type, str)
        
        # Return the type directly - we'll handle optionality in the field definition
        return python_type
    
    @classmethod
    def _get_sqlalchemy_type(cls, field_schema: Dict[str, Any]):
        """Get SQLAlchemy column type from field schema."""
        field_type = field_schema.get("type", "string")
        
        # Handle special formats
        if field_type == "string":
            format_type = field_schema.get("format")
            if format_type == "datetime":
                return DateTime
            elif field_schema.get("maxLength", 0) > 500 or field_schema.get("description", "").lower().find("text") != -1:
                return Text
            else:
                max_length = field_schema.get("maxLength", 255)
                return String(max_length)
        
        return cls.SQLALCHEMY_TYPE_MAPPING.get(field_type, String)
    
    @classmethod
    def _get_default_value(cls, field_schema: Dict[str, Any], is_required: bool):
        """Get default value for a field."""
        if is_required and "default" not in field_schema:
            return ...  # Ellipsis indicates required field
        
        return field_schema.get("default", None)


class APIRegistry:
    """Registry to keep track of created dynamic APIs."""
    
    def __init__(self):
        self.apis: Dict[str, Dict[str, Any]] = {}
    
    def register_api(self, name: str, model: Type[BaseModel], create_model: Type[BaseModel], 
                    table: sqlalchemy.Table, schema: Dict[str, Any]):
        """Register a dynamic API."""
        self.apis[name] = {
            "model": model,
            "create_model": create_model,
            "table": table,
            "schema": schema,
            "created_at": datetime.now()
        }
    
    def get_api(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a registered API by name."""
        return self.apis.get(name)
    
    def list_apis(self) -> List[str]:
        """List all registered API names."""
        return list(self.apis.keys())
    
    def remove_api(self, name: str) -> bool:
        """Remove a registered API."""
        if name in self.apis:
            del self.apis[name]
            return True
        return False


# Global registry instance
api_registry = APIRegistry()