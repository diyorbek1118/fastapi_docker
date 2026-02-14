"""
Logging Middleware - Har bir requestni avtomatik log qiladi.

Vazifasi:
- Request kelganini log qilish
- Response status log qilish
- Client IP, method, path
- Request ID bilan birlashtirilgan

Foyda:
- Har bir request tarixi
- Security audit
- Debugging oson
- Har endpointda logger.info() yozish shart emas
"""
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from datetime import datetime

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log all requests and responses.
    
    Usage:
        app.add_middleware(LoggingMiddleware)
    
    Logs format:
        INFO [req-id] IP - METHOD PATH - STATUS CODE - TIME
    
    Example:
        INFO [a1b2c3] 127.0.0.1 - GET /api/v1/posts - 200 OK - 0.045s
        ERROR [d4e5f6] 192.168.1.5 - POST /api/v1/auth/login - 401 - 0.012s
    """
    
    async def dispatch(self, request: Request, call_next):
        # 1. Get request info
        request_id = getattr(request.state, "request_id", "no-id")
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # 2. Log incoming request
        logger.info(
            f"[{request_id}] {client_ip} - {method} {path} - Started"
        )
        
        # 3. Process request
        start_time = datetime.utcnow()
        
        try:
            response = await call_next(request)
            
            # 4. Log successful response
            process_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Different log level based on status code
            if response.status_code >= 500:
                logger.error(
                    f"[{request_id}] {client_ip} - {method} {path} - "
                    f"{response.status_code} - {process_time:.3f}s"
                )
            elif response.status_code >= 400:
                logger.warning(
                    f"[{request_id}] {client_ip} - {method} {path} - "
                    f"{response.status_code} - {process_time:.3f}s"
                )
            else:
                logger.info(
                    f"[{request_id}] {client_ip} - {method} {path} - "
                    f"{response.status_code} - {process_time:.3f}s"
                )
            
            return response
            
        except Exception as e:
            # 5. Log exceptions
            process_time = (datetime.utcnow() - start_time).total_seconds()
            logger.exception(
                f"[{request_id}] {client_ip} - {method} {path} - "
                f"EXCEPTION - {process_time:.3f}s - {str(e)}"
            )
            raise


# ========================================
# OPTIONAL: Structured Logging
# ========================================
class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Advanced version with structured logging (JSON format).
    
    Better for log aggregation tools (ELK, Datadog, etc.)
    """
    
    async def dispatch(self, request: Request, call_next):
        import json
        
        request_id = getattr(request.state, "request_id", "no-id")
        start_time = datetime.utcnow()
        
        try:
            response = await call_next(request)
            process_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Structured log (JSON)
            log_data = {
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "client_ip": request.client.host if request.client else "unknown",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": round(process_time, 3),
                "user_agent": request.headers.get("user-agent", "unknown")
            }
            
            logger.info(json.dumps(log_data))
            
            return response
            
        except Exception as e:
            process_time = (datetime.utcnow() - start_time).total_seconds()
            
            log_data = {
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "client_ip": request.client.host if request.client else "unknown",
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "process_time": round(process_time, 3),
                "error": str(e),
                "error_type": type(e).__name__
            }
            
            logger.error(json.dumps(log_data))
            raise