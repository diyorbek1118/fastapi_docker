"""
Request ID Middleware - Har bir requestga unique ID beradi.

Vazifasi:
- Har bir requestga UUID generate qiladi
- Request.state ga saqlab qo'yadi
- Response headerga qo'shadi
- Logging uchun ishlatiladi

Foyda:
- Loglarni kuzatish oson
- Debugging oson  
- Production da muammolarni tezda topish
"""
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request.
    
    Usage:
        app.add_middleware(RequestIDMiddleware)
    
    Example:
        Request comes in → Generate UUID → Add to request.state → Add to response header
    """
    
    async def dispatch(self, request: Request, call_next):
        # 1. Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # 2. Save to request.state (har joydan access qilish uchun)
        request.state.request_id = request_id
        
        # 3. Process request
        response = await call_next(request)
        
        # 4. Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


# ========================================
# QANDAY ISHLATISH (HELPER FUNCTION)
# ========================================
def get_request_id(request: Request) -> str:
    """
    Get request ID from request state.
    
    Usage:
        from middleware.request_id import get_request_id
        
        @router.get("/posts")
        def get_posts(request: Request):
            request_id = get_request_id(request)
            logger.info(f"[{request_id}] Fetching posts...")
    """
    return getattr(request.state, "request_id", "no-request-id")