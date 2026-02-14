from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer
from sqlalchemy.exc import SQLAlchemyError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator

from core.config import settings
from core.logging_config import setup_logging
from core.error_handlers import (
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)
from api.v1.routes import post as post_v1, auth
from api.v2.routes import post as post_v2

# ========================================
# ⚡ MIDDLEWARE IMPORTS (YANGI!)
# ========================================
from middleware import (
    RequestIDMiddleware,
    TimingMiddleware,
    LoggingMiddleware
)

import logging

# ========================================
# SETUP LOGGING
# ========================================
setup_logging()
logger = logging.getLogger(__name__)

# ========================================
# RATE LIMITER
# ========================================
limiter = Limiter(key_func=get_remote_address)

# ========================================
# CREATE APP (FAQAT BIR MARTA!)
# ========================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

Instrumentator().instrument(app).expose(app)

# ========================================
# LIMITER
# ========================================
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ========================================
# SECURITY
# ========================================
security = HTTPBearer()

# ========================================
# EXCEPTION HANDLERS
# ========================================
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ========================================
# ⚡ MIDDLEWARE (YANGI!)
# Tartib MUHIM: birinchi qo'shilgan oxirgi ishlaydi
# ========================================
# 1. Request ID - eng birinchi bo'lishi kerak
app.add_middleware(RequestIDMiddleware)

# 2. Timing - request ID dan keyin
app.add_middleware(TimingMiddleware)

# 3. Logging - oxirida (request ID va timing dan foydalanadi)
app.add_middleware(LoggingMiddleware)

# ========================================
# CORS (MIDDLEWARE hisoblanadi)
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# ========================================
# ROUTERS
# ========================================
app.include_router(post_v1.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(post_v2.router, prefix="/api/v2")

# ========================================
# ROOT ENDPOINT
# ========================================
@app.get("/")
def read_root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running"
    }

# ========================================
# HEALTH CHECK
# ========================================
@app.get("/health")
def health_check():
    from core.database import test_database_connection
    db_status = "healthy" if test_database_connection() else "unhealthy"
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }

# ========================================
# STARTUP EVENT
# ========================================
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info("⚡ Middleware enabled:")
    logger.info("  - RequestIDMiddleware ✅")
    logger.info("  - TimingMiddleware ✅")
    logger.info("  - LoggingMiddleware ✅")
    logger.info("=" * 60)

# ========================================
# SHUTDOWN EVENT
# ========================================
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.APP_NAME}")