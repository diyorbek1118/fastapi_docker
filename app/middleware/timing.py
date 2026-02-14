"""
Timing Middleware - Request processing vaqtini o'lchaydi.

Vazifasi:
- Request qancha vaqt olgani
- Response headerga qo'shadi
- Prometheus metrics uchun
- Slow endpoints topish

Foyda:
- Performance monitoring
- Bottleneck topish
- Optimization kerakli joylarni aniqlash
"""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to measure request processing time.
    
    Usage:
        app.add_middleware(TimingMiddleware)
    
    Adds headers:
        X-Process-Time: Time in seconds (float)
    
    Example:
        GET /api/v1/posts
        Response Headers:
            X-Process-Time: 0.045
            X-Request-ID: a1b2c3d4...
    """
    
    async def dispatch(self, request: Request, call_next):
        # 1. Start timer
        start_time = time.time()
        
        # 2. Process request
        response = await call_next(request)
        
        # 3. Calculate processing time
        process_time = time.time() - start_time
        
        # 4. Add to response headers (seconds)
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        
        # 5. Log slow requests (> 1 second)
        if process_time > 1.0:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(
                f"[{request_id}] SLOW REQUEST: "
                f"{request.method} {request.url.path} "
                f"took {process_time:.3f}s"
            )
        
        return response


# ========================================
# HELPER FUNCTIONS
# ========================================
def get_process_time(response) -> float:
    """
    Get process time from response headers.
    
    Usage:
        process_time = get_process_time(response)
        if process_time > 0.5:
            logger.warning("Slow request!")
    """
    return float(response.headers.get("X-Process-Time", 0))