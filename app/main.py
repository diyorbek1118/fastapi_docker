from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine
from core.config import settings
from models.post import Post
from api.v1.routes import post

# Database tables yaratish
Base.metadata.create_all(bind=engine)

# FastAPI app yaratish
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Routers
app.include_router(post.router, prefix="/api/v1")


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


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print(f"Shutting down {settings.APP_NAME}")