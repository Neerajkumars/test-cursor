from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import uvicorn

from .config import settings
from .database import connect_database, disconnect_database, create_tables
from .crud_manager import DynamicCRUDManager


# Pydantic models for API management
class CreateAPIRequest(BaseModel):
    """Request model for creating a dynamic API."""
    name: str = Field(..., description="Name of the API", min_length=1, max_length=50)
    schema: Dict[str, Any] = Field(..., description="JSON schema for the API")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options for the API")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "products",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Product name"},
                        "price": {"type": "number", "description": "Product price"},
                        "description": {"type": "string", "description": "Product description"},
                        "category": {"type": "string", "description": "Product category"},
                        "in_stock": {"type": "boolean", "default": True}
                    },
                    "required": ["name", "price"]
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
        }


class APIResponse(BaseModel):
    """Response model for API operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A dynamic microservice that generates CRUD APIs from JSON schemas",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize CRUD manager
crud_manager = DynamicCRUDManager(app)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    await connect_database()
    create_tables()
    print(f"🚀 {settings.app_name} v{settings.app_version} started successfully!")
    print(f"📚 API Documentation: http://localhost:8000{settings.docs_url}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await disconnect_database()
    print("👋 Application shutdown complete.")


# API Management Endpoints
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "description": "Dynamic API microservice using FastAPI CRUD Router",
        "docs_url": settings.docs_url,
        "management_endpoints": {
            "create_api": "POST /manage/apis",
            "list_apis": "GET /manage/apis",
            "get_api": "GET /manage/apis/{name}",
            "delete_api": "DELETE /manage/apis/{name}"
        }
    }


@app.post("/manage/apis", response_model=APIResponse, tags=["API Management"])
async def create_api(request: CreateAPIRequest):
    """Create a new dynamic API from JSON schema."""
    try:
        result = await crud_manager.create_dynamic_api(
            name=request.name,
            schema=request.schema,
            options=request.options
        )
        
        return APIResponse(
            success=True,
            message=f"API '{request.name}' created successfully",
            data=result
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/manage/apis", response_model=APIResponse, tags=["API Management"])
async def list_apis():
    """List all dynamic APIs."""
    try:
        result = crud_manager.list_apis()
        
        return APIResponse(
            success=True,
            message="APIs retrieved successfully",
            data=result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/manage/apis/{name}", response_model=APIResponse, tags=["API Management"])
async def get_api(name: str):
    """Get information about a specific dynamic API."""
    try:
        result = crud_manager.get_api_info(name)
        
        return APIResponse(
            success=True,
            message=f"API '{name}' information retrieved successfully",
            data=result
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/manage/apis/{name}", response_model=APIResponse, tags=["API Management"])
async def delete_api(name: str):
    """Delete a dynamic API."""
    try:
        result = await crud_manager.delete_api(name)
        
        return APIResponse(
            success=True,
            message=f"API '{name}' deleted successfully",
            data=result
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name, "version": settings.app_version}


# Schema validation endpoint
@app.post("/manage/validate-schema", response_model=APIResponse, tags=["API Management"])
async def validate_schema(schema: Dict[str, Any] = Body(...)):
    """Validate a JSON schema without creating an API."""
    try:
        from .config import DynamicAPIConfig
        
        config = DynamicAPIConfig("test", schema)
        is_valid = config.validate_schema()
        
        if is_valid:
            return APIResponse(
                success=True,
                message="Schema is valid",
                data={"valid": True, "schema": schema}
            )
        else:
            return APIResponse(
                success=False,
                message="Schema is invalid",
                data={"valid": False, "errors": ["Schema must contain 'properties' field"]}
            )
    
    except Exception as e:
        return APIResponse(
            success=False,
            message="Schema validation failed",
            data={"valid": False, "errors": [str(e)]}
        )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )