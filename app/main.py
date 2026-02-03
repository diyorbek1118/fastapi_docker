from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine
from core.config import settings
from models.post import Post
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from api.v1.routes import post, auth

from core.config import settings
from core.error_handlers import (
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)

from core.logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

# Database tables yaratish
#Base.metadata.create_all(bind=engine)

# FastAPI app yaratish
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# ROUTERS
app.include_router(post.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")  


# Root endpoint
@app.get("/")
def read_root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running"
    }


# Health check endpoint
@app.get("/health")
def health_check():
    from core.database import test_database_connection
    
    db_status = "healthy" if test_database_connection() else "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Starting {settings.APP_NAME}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print(f"Shutting down {settings.APP_NAME}")