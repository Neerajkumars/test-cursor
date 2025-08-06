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
        """Create a Pydantic model from JSON schema.
        
        This method is fully compatible with Pydantic v2 and uses only
        public APIs to avoid internal implementation dependencies.
        """
        
        if "properties" not in schema:
            raise ValueError("Schema must contain 'properties' field")
        
        properties = schema["properties"]
        required_fields = schema.get("required", [])
        
        # Build field definitions using a Pydantic v2 compatible approach
        fields = {}
        
        # Add id field first if not present
        if "id" not in properties:
            fields["id"] = (Optional[int], Field(None, description="Unique identifier"))
        
        try:
            for field_name, field_schema in properties.items():
                # Get base Python type using our safe method
                python_type = cls._get_python_type_simple(field_schema)
                is_required = field_name in required_fields
                default_value = field_schema.get("default")
                description = field_schema.get("description", "")
                
                # Handle field definition based on requirements and defaults
                if is_required and default_value is None:
                    # Required field without default
                    fields[field_name] = (python_type, Field(..., description=description))
                elif default_value is not None:
                    # Field with default value (required fields with defaults are allowed)
                    fields[field_name] = (python_type, Field(default=default_value, description=description))
                else:
                    # Optional field without default
                    fields[field_name] = (Optional[python_type], Field(None, description=description))
            
            # Create the model using Pydantic's create_model function
            return create_model(name, **fields, __base__=base_class)
            
        except Exception as e:
            raise ValueError(f"Failed to create Pydantic model '{name}': {str(e)}")
    
    @classmethod
    def create_create_model(cls, base_model: Type[BaseModel], name: str) -> Type[BaseModel]:
        """Create a 'Create' version of the model (without id field).
        
        This method is compatible with Pydantic v2 and avoids accessing
        internal FieldInfo attributes that changed between versions.
        """
        fields = {}
        
        # Get model schema to rebuild without id - this is safe in Pydantic v2
        try:
            model_schema = base_model.model_json_schema()
            properties = model_schema.get("properties", {})
            required_fields = model_schema.get("required", [])
            
            for field_name, field_props in properties.items():
                if field_name != "id":  # Exclude id field for create operations
                    # Determine the Python type from schema
                    python_type = cls._get_python_type_from_json_schema(field_props)
                    is_required = field_name in required_fields
                    default_value = field_props.get("default")
                    description = field_props.get("description", "")
                    
                    # Create field definition based on requirements
                    if is_required and default_value is None:
                        # Required field without default
                        fields[field_name] = (python_type, Field(..., description=description))
                    elif default_value is not None:
                        # Field with default value (can be required or optional)
                        fields[field_name] = (python_type, Field(default=default_value, description=description))
                    else:
                        # Optional field without default
                        fields[field_name] = (Optional[python_type], Field(None, description=description))
            
            return create_model(f"{name}Create", **fields)
            
        except Exception as e:
            raise ValueError(f"Failed to create Create model for {name}: {str(e)}")
    
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
    def _get_python_type_simple(cls, field_schema: Dict[str, Any]) -> Type:
        """Get Python type for Pydantic model from field schema (simplified)."""
        field_type = field_schema.get("type", "string")
        
        # Handle special formats
        if field_type == "string":
            format_type = field_schema.get("format")
            if format_type == "datetime":
                return datetime
            elif format_type == "uuid":
                return str
            return str
        
        # Handle arrays
        if field_type == "array":
            items_schema = field_schema.get("items", {})
            item_type = cls._get_python_type_simple(items_schema)
            return List[item_type]
        
        # Get base type
        return cls.TYPE_MAPPING.get(field_type, str)
    
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
    def _get_python_type_from_json_schema(cls, json_schema: Dict[str, Any]) -> Type:
        """Convert JSON schema property back to Python type.
        
        This method safely handles JSON schema to Python type conversion
        without relying on Pydantic internal structures.
        """
        schema_type = json_schema.get("type", "string")
        
        try:
            if schema_type == "string":
                json_format = json_schema.get("format")
                if json_format in ["date-time", "datetime"]:
                    return datetime
                elif json_format == "uuid":
                    return str
                return str
            elif schema_type == "integer":
                return int
            elif schema_type == "number":
                return float
            elif schema_type == "boolean":
                return bool
            elif schema_type == "array":
                items = json_schema.get("items", {})
                if items:
                    item_type = cls._get_python_type_from_json_schema(items)
                    return List[item_type]
                else:
                    # Default to list of strings if no items specified
                    return List[str]
            elif schema_type == "object":
                return dict
            else:
                # Default to string for unknown types
                return str
                
        except Exception:
            # Fallback to string type if anything goes wrong
            return str
    
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