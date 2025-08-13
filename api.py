import os
import sys
import logging
import traceback
from contextlib import asynccontextmanager
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
import uvicorn

# Import the crew after setting up the path
try:
    from src.open_source.crew import OpenSourceCrew
except ImportError as e:
    print(f"Import error: {e}")
    # Add current directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from src.open_source.crew import OpenSourceCrew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Pydantic Models
class BusinessRequirementRequest(BaseModel):
    """Request model for business requirement analysis"""
    business_requirement: str = Field(
        ..., 
        min_length=10, 
        max_length=2000,
        description="Business requirement description for open source project research",
        examples=["I need a Python web framework for building REST APIs with authentication, database ORM, and automatic API documentation"]
    )
    
    @field_validator('business_requirement')
    @classmethod
    def validate_requirement(cls, v):
        if not v or not v.strip():
            raise ValueError('Business requirement cannot be empty')
        return v.strip()

class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    status: str = Field(description="Status of the analysis")
    message: str = Field(description="Status message")
    result: str = Field(description="Analysis result")
    timestamp: datetime = Field(description="Analysis timestamp")
    execution_time_seconds: float = Field(description="Execution time in seconds")

class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    message: str = Field(description="Error message")
    timestamp: datetime = Field(description="Error timestamp")
    detail: str = Field(default="", description="Detailed error information")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = "healthy"
    timestamp: datetime = Field(description="Health check timestamp")
    version: str = "1.0.0"
    environment: str = Field(description="Current environment")

# Global variables for environment validation
REQUIRED_ENV_VARS = ["GEMINI_API_KEY", "SERPER_API_KEY"]

def validate_environment():
    """Validate required environment variables"""
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        return False, error_msg
    
    logger.info("Environment validation successful")
    return True, "Environment OK"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Open Source Research API...")
    
    # Validate required environment variables
    is_valid, message = validate_environment()
    if not is_valid:
        logger.warning(f"Environment validation failed: {message}")
        # Don't fail startup, but log the warning
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Open Source Research API...")

# FastAPI application setup
app = FastAPI(
    title="Open Source Project Research API",
    description="AI-powered API for discovering and analyzing open-source projects based on business requirements",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.now()
    
    # Log request details
    client_host = request.client.host if request.client else 'unknown'
    logger.info(f"Request: {request.method} {request.url.path} from {client_host}")
    
    response = await call_next(request)
    
    # Log response details
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "detail": f"HTTP {exc.status_code} error"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    error_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.error(f"Unhandled exception [{error_id}]: {str(exc)}")
    logger.error(f"Traceback [{error_id}]: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal server error occurred",
            "timestamp": datetime.now().isoformat(),
            "detail": f"Error ID: {error_id}"
        }
    )

# API Routes
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Open Source Project Research API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "analyze": "/analyze",
            "health": "/health",
            "version": "/version",
            "status": "/status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    is_valid, env_message = validate_environment()
    
    return {
        "status": "healthy" if is_valid else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "environment_check": env_message
    }

@app.post("/analyze")
async def analyze_requirement(request: BusinessRequirementRequest):
    """
    Analyze business requirements and find suitable open-source projects
    
    This endpoint uses AI agents to:
    1. Analyze the business requirement
    2. Research suitable open-source projects on GitHub
    3. Evaluate and rank the projects based on multiple criteria
    
    Returns detailed analysis with project recommendations.
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting analysis for requirement: {request.business_requirement[:100]}...")
        
        # Validate environment variables
        is_valid, env_message = validate_environment()
        if not is_valid:
            raise HTTPException(
                status_code=500,
                detail=f"Server configuration error: {env_message}"
            )
        
        # Get API keys from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not configured"
            )
        
        # Create and run the CrewAI analysis
        logger.info("Creating CrewAI instance...")
        
        # Disable CrewAI telemetry to avoid connection issues
        os.environ["OTEL_SDK_DISABLED"] = "true"
        os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
        
        crew = OpenSourceCrew(
            business_requirement=request.business_requirement,
            gemini_api_key=gemini_api_key
        )
        
        logger.info("Executing CrewAI analysis...")
        result = crew.run()
        
        # Check if result is None or empty
        if not result or str(result).strip() == "":
            raise HTTPException(
                status_code=500,
                detail="AI analysis returned empty result. This might be due to API rate limits or connectivity issues."
            )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Analysis completed successfully in {execution_time:.2f} seconds")
        
        return {
            "status": "success",
            "message": "Analysis completed successfully",
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "execution_time_seconds": execution_time
        }
        
    except ValueError as e:
        # Handle known validation errors
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Handle unexpected errors
        error_msg = str(e)
        logger.error(f"Analysis failed: {error_msg}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Check for specific API-related errors
        if any(keyword in error_msg.lower() for keyword in ['overloaded', 'unavailable', '503', 'rate limit', 'quota']):
            raise HTTPException(
                status_code=503,
                detail="AI service is temporarily unavailable. Please try again in a few minutes."
            )
        elif any(keyword in error_msg.lower() for keyword in ['api key', 'authentication', 'permission', 'forbidden']):
            raise HTTPException(
                status_code=500,
                detail="Server configuration error: Invalid API key configuration"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"An unexpected error occurred during analysis: {error_msg}"
            )

@app.get("/version")
async def get_version():
    """Get API version information"""
    return {
        "version": "1.0.0",
        "build_date": "2025-01-13",
        "python_version": sys.version,
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/status")
async def get_status():
    """Get detailed service status"""
    is_valid, env_message = validate_environment()
    
    return {
        "service": "Open Source Project Research API",
        "status": "operational" if is_valid else "degraded",
        "timestamp": datetime.now().isoformat(),
        "environment_variables_configured": is_valid,
        "environment_check": env_message,
        "required_env_vars": REQUIRED_ENV_VARS,
        "current_working_directory": os.getcwd(),
        "python_path": sys.path[:3]  # First 3 paths for debugging
    }

# For local development
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        reload=False
    )