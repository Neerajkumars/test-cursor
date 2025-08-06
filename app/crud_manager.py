from fastapi import FastAPI, HTTPException
from fastapi_crudrouter import DatabasesCRUDRouter
from typing import Dict, Any, Optional, List
import sqlalchemy

from .models import DynamicModelGenerator, api_registry
from .database import database, metadata, create_tables
from .config import settings, DynamicAPIConfig


class DynamicCRUDManager:
    """Manager for creating and managing dynamic CRUD routers."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.active_routers: Dict[str, DatabasesCRUDRouter] = {}
    
    async def create_dynamic_api(self, name: str, schema: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new dynamic API from JSON schema."""
        
        # Validate input
        if name in api_registry.list_apis():
            raise HTTPException(status_code=400, detail=f"API '{name}' already exists")
        
        if len(api_registry.list_apis()) >= settings.max_dynamic_apis:
            raise HTTPException(status_code=400, detail="Maximum number of dynamic APIs reached")
        
        # Create API configuration
        config = DynamicAPIConfig(name, schema, options)
        
        if not config.validate_schema():
            raise HTTPException(status_code=400, detail="Invalid JSON schema provided")
        
        try:
            # Generate Pydantic models
            model_name = name.capitalize()
            pydantic_model = DynamicModelGenerator.create_pydantic_model(model_name, schema)
            create_model = DynamicModelGenerator.create_create_model(pydantic_model, model_name)
            
            # Generate SQLAlchemy table
            table = DynamicModelGenerator.create_sqlalchemy_table(name, schema, metadata)
            
            # Create the table in database
            table.create(bind=sqlalchemy.create_engine(settings.database_url), checkfirst=True)
            
            # Create CRUD router
            router_options = self._get_router_options(options or {})
            router = DatabasesCRUDRouter(
                schema=pydantic_model,
                create_schema=create_model,
                table=table,
                database=database,
                prefix=config.get_prefix(),
                **router_options
            )
            
            # Register the API
            api_registry.register_api(name, pydantic_model, create_model, table, schema)
            
            # Add router to FastAPI app
            self.app.include_router(router, tags=[name])
            self.active_routers[name] = router
            
            return {
                "name": name,
                "prefix": config.get_prefix(),
                "schema": schema,
                "status": "created",
                "endpoints": self._get_endpoint_info(config.get_prefix())
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create API: {str(e)}")
    
    def get_api_info(self, name: str) -> Dict[str, Any]:
        """Get information about a specific dynamic API."""
        api_info = api_registry.get_api(name)
        if not api_info:
            raise HTTPException(status_code=404, detail=f"API '{name}' not found")
        
        config = DynamicAPIConfig(name, api_info["schema"])
        
        return {
            "name": name,
            "prefix": config.get_prefix(),
            "schema": api_info["schema"],
            "created_at": api_info["created_at"].isoformat(),
            "endpoints": self._get_endpoint_info(config.get_prefix())
        }
    
    def list_apis(self) -> Dict[str, Any]:
        """List all dynamic APIs."""
        apis = []
        for name in api_registry.list_apis():
            try:
                api_info = self.get_api_info(name)
                apis.append(api_info)
            except HTTPException:
                continue  # Skip if API info cannot be retrieved
        
        return {
            "apis": apis,
            "total": len(apis),
            "max_allowed": settings.max_dynamic_apis
        }
    
    async def delete_api(self, name: str) -> Dict[str, Any]:
        """Delete a dynamic API."""
        if name not in api_registry.list_apis():
            raise HTTPException(status_code=404, detail=f"API '{name}' not found")
        
        try:
            # Remove from registry
            api_registry.remove_api(name)
            
            # Remove router (Note: FastAPI doesn't support removing routers dynamically,
            # so we'll mark it as removed and recommend restarting the service)
            if name in self.active_routers:
                del self.active_routers[name]
            
            # Note: The table will remain in the database for data persistence
            # In a production environment, you might want to implement table cleanup
            
            return {
                "name": name,
                "status": "deleted",
                "message": "API removed from registry. Service restart recommended for complete removal."
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete API: {str(e)}")
    
    def _get_router_options(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Get router options from user-provided options."""
        router_options = {}
        
        # Pagination settings
        if "pagination" in options:
            pagination = options["pagination"]
            if pagination.get("enabled", True):
                router_options["paginate"] = pagination.get("size", settings.default_pagination_size)
        
        # Route disabling
        route_options = options.get("routes", {})
        for route_name, enabled in route_options.items():
            if route_name in ["get_all", "get_one", "create", "update", "delete_one", "delete_all"]:
                router_options[f"{route_name}_route"] = enabled
        
        return router_options
    
    def _get_endpoint_info(self, prefix: str) -> List[Dict[str, str]]:
        """Get endpoint information for a given prefix."""
        return [
            {"method": "GET", "path": prefix, "description": "Get all items"},
            {"method": "POST", "path": prefix, "description": "Create a new item"},
            {"method": "GET", "path": f"{prefix}/{{item_id}}", "description": "Get item by ID"},
            {"method": "PUT", "path": f"{prefix}/{{item_id}}", "description": "Update item by ID"},
            {"method": "DELETE", "path": f"{prefix}/{{item_id}}", "description": "Delete item by ID"},
            {"method": "DELETE", "path": prefix, "description": "Delete all items"}
        ]