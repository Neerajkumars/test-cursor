from pydantic_settings import BaseSettings
from typing import Dict, Any, Optional
import os


class Settings(BaseSettings):
    """Application settings configuration."""
    
    app_name: str = "Dynamic API Microservice"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database settings
    database_url: str = "postgresql://user:password@localhost:5432/dynamic_api_db"
    
    # API settings
    api_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # Dynamic API settings
    max_dynamic_apis: int = 50
    default_pagination_size: int = 20
    max_pagination_size: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


class DynamicAPIConfig:
    """Configuration for dynamic API generation."""
    
    def __init__(self, name: str, schema: Dict[str, Any], options: Optional[Dict[str, Any]] = None):
        self.name = name
        self.schema = schema
        self.options = options or {}
        
    def get_prefix(self) -> str:
        """Get the API prefix for this dynamic API."""
        return f"/{self.name.lower()}"
    
    def get_table_name(self) -> str:
        """Get the database table name for this dynamic API."""
        return f"dynamic_{self.name.lower()}"
    
    def validate_schema(self) -> bool:
        """Validate the provided schema."""
        if not isinstance(self.schema, dict):
            return False
        
        if "properties" not in self.schema:
            return False
            
        if not isinstance(self.schema["properties"], dict):
            return False
            
        return True