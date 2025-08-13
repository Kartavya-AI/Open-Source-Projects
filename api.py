import os
import sys
import logging
import traceback
from contextlib import asynccontextmanager
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

from src.open_source.crew import OpenSourceCrew

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
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
        example="I need a Python web framework for building REST APIs with authentication, database ORM, and automatic API documentation"
    )
    
    @validator('business_requirement')
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Open Source Research API...")
    
    # Validate required environment variables
    missing_vars = []
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    logger.info("Environment validation successful")
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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Custom middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.now()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    
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
        content=ErrorResponse(
            message=exc.detail,
            timestamp=datetime.now(),
            detail=f"HTTP {exc.status_code} error"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    error_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.error(f"Unhandled exception [{error_id}]: {str(exc)}")
    logger.error(f"Traceback [{error_id}]: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="An internal server error occurred",
            timestamp=datetime.now(),
            detail=f"Error ID: {error_id}"
        ).dict()
    )

# API Routes
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Open Source Project Research API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(),
        "documentation": "/docs",
        "health_check": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Cloud Run"""
    return HealthResponse(
        timestamp=datetime.now(),
        environment=os.getenv("ENVIRONMENT", "production")
    )

@app.post("/analyze", response_model=AnalysisResponse)
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
        
        # Validate environment variables again (safety check)
        missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
        if missing_vars:
            raise HTTPException(
                status_code=500,
                detail=f"Server configuration error: Missing environment variables: {', '.join(missing_vars)}"
            )
        
        # Create and run the CrewAI analysis
        crew = OpenSourceCrew(
            business_requirement=request.business_requirement,
            gemini_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        logger.info("Executing CrewAI analysis...")
        result = crew.run()
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Analysis completed successfully in {execution_time:.2f} seconds")
        
        return AnalysisResponse(
            status="success",
            message="Analysis completed successfully",
            result=result,
            timestamp=datetime.now(),
            execution_time_seconds=execution_time
        )
        
    except ValueError as e:
        # Handle known validation errors
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Handle unexpected errors
        error_msg = str(e)
        logger.error(f"Analysis failed: {error_msg}")
        
        # Check for specific API-related errors
        if any(keyword in error_msg.lower() for keyword in ['overloaded', 'unavailable', '503', 'rate limit', 'quota']):
            raise HTTPException(
                status_code=503,
                detail="AI service is temporarily unavailable. Please try again in a few minutes."
            )
        elif any(keyword in error_msg.lower() for keyword in ['api key', 'authentication', 'permission', 'forbidden']):
            raise HTTPException(
                status_code=500,
                detail="Server configuration error. Please contact support."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred during analysis. Please try again."
            )

@app.post("/analyze-async", response_model=Dict[str, Any])
async def analyze_requirement_async(request: BusinessRequirementRequest, background_tasks: BackgroundTasks):
    """
    Start asynchronous analysis of business requirements
    
    This endpoint starts the analysis in the background and returns immediately.
    In a production environment, you would typically use a message queue
    and provide a way to check the status of the analysis.
    """
    task_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    def run_analysis():
        """Background task to run the analysis"""
        try:
            logger.info(f"Background analysis started for task {task_id}")
            crew = OpenSourceCrew(
                business_requirement=request.business_requirement,
                gemini_api_key=os.getenv("GEMINI_API_KEY")
            )
            result = crew.run()
            logger.info(f"Background analysis completed for task {task_id}")
            # In production, you would store this result in a database or cache
        except Exception as e:
            logger.error(f"Background analysis failed for task {task_id}: {str(e)}")
    
    background_tasks.add_task(run_analysis)
    
    return {
        "status": "accepted",
        "message": "Analysis started in background",
        "task_id": task_id,
        "timestamp": datetime.now(),
        "note": "This is a demonstration endpoint. In production, use a proper queue system."
    }

# Additional utility endpoints
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
    return {
        "service": "Open Source Project Research API",
        "status": "operational",
        "timestamp": datetime.now(),
        "uptime": "Service started",
        "environment_variables_configured": all(os.getenv(var) for var in REQUIRED_ENV_VARS),
        "required_env_vars": REQUIRED_ENV_VARS
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )