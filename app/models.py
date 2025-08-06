from pydantic import BaseModel, create_model, Field
from typing import Dict, Any, Type, Optional, Union, List
import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

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
            field_type = cls._get_pydantic_type(field_schema)
            default_value = cls._get_default_value(field_schema, field_name in required_fields)
            
            # Create field with validation
            if default_value is ...:  # Required field
                fields[field_name] = (field_type, Field(..., description=field_schema.get("description", "")))
            else:
                fields[field_name] = (field_type, Field(default=default_value, description=field_schema.get("description", "")))
        
        # Add id field if not present
        if "id" not in fields:
            fields["id"] = (Optional[int], Field(None, description="Unique identifier"))
        
        # Create the model
        return create_model(name, **fields, __base__=base_class)
    
    @classmethod
    def create_create_model(cls, base_model: Type[BaseModel], name: str) -> Type[BaseModel]:
        """Create a 'Create' version of the model (without id field)."""
        fields = {}
        
        for field_name, field_info in base_model.model_fields.items():
            if field_name != "id":  # Exclude id field for create operations
                field_type = field_info.annotation
                default = field_info.default if field_info.default is not ... else ...
                fields[field_name] = (field_type, Field(default, description=field_info.description))
        
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
        field_type = field_schema.get("type", "string")
        
        # Handle special formats
        if field_type == "string":
            format_type = field_schema.get("format")
            if format_type == "datetime":
                return Optional[datetime]
            elif format_type == "uuid":
                return Optional[str]
        
        # Handle arrays
        if field_type == "array":
            items_schema = field_schema.get("items", {})
            item_type = cls._get_pydantic_type(items_schema)
            return Optional[List[item_type]]
        
        # Get base type
        python_type = cls.TYPE_MAPPING.get(field_type, str)
        
        # Make optional if not required (will be handled in create_pydantic_model)
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