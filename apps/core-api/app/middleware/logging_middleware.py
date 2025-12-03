"""
Middleware to add logging context to requests
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from phi_utils.logging import ContextLogger
import logging

logger = logging.getLogger("core-api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Add request context to logs"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract context from request state if available
        context = {}
        if hasattr(request.state, "user"):
            user = request.state.user
            context["user_id"] = str(user.id) if hasattr(user, "id") else None
        
        if hasattr(request.state, "org_id"):
            context["org_id"] = str(request.state.org_id)
        
        if hasattr(request.state, "agent_id"):
            context["agent_id"] = str(request.state.agent_id)
        
        ctx_logger = ContextLogger(logger, **context)
        
        # Log request
        ctx_logger.info(
            f"{request.method} {request.url.path}",
            extra_data={"method": request.method, "path": request.url.path}
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            ctx_logger.info(
                f"{request.method} {request.url.path} - {response.status_code}",
                extra_data={
                    "status_code": response.status_code,
                    "process_time": process_time
                }
            )
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            ctx_logger.exception(
                f"Error processing {request.method} {request.url.path}",
                extra_data={"process_time": process_time}
            )
            raise


