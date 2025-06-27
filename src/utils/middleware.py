"""
Middleware components for the Patient Risk Predictor application.

This module provides middleware for request logging, correlation ID tracking,
and error handling to improve observability and debugging.
"""

import time
from typing import Callable, List, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .logging_config import clear_correlation_id, get_logger, set_correlation_id

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging and correlation ID tracking."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process requests with logging and correlation tracking.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain

        Returns:
            HTTP response
        """
        # Generate correlation ID for this request
        correlation_id = set_correlation_id()

        # Extract request information
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log request start
        start_time = time.time()
        logger.info(
            "Request started",
            extra={
                "event": "request_start",
                "method": method,
                "url": url,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "request_size": request.headers.get("content-length", 0),
            },
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log successful response
            logger.info(
                "Request completed",
                extra={
                    "event": "request_complete",
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000, 2),
                    "response_size": response.headers.get("content-length", 0),
                },
            )

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            return response

        except Exception as e:
            # Calculate processing time for error
            process_time = time.time() - start_time

            # Log error
            logger.error(
                "Request failed",
                extra={
                    "event": "request_error",
                    "method": method,
                    "url": url,
                    "process_time_ms": round(process_time * 1000, 2),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
                exc_info=True,
            )

            # Re-raise the exception to be handled by FastAPI
            raise

        finally:
            # Clean up correlation ID
            clear_correlation_id()


class HealthCheckLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that reduces logging noise from health check endpoints."""

    def __init__(self, app, health_check_paths: Optional[List[str]] = None):
        """
        Initialize health check middleware.

        Args:
            app: FastAPI application instance
            health_check_paths: List of paths to treat as health checks
        """
        super().__init__(app)
        self.health_check_paths = health_check_paths or ["/", "/health", "/healthz"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process requests with reduced logging for health checks.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain

        Returns:
            HTTP response
        """
        # Check if this is a health check request
        is_health_check = any(request.url.path.startswith(path) for path in self.health_check_paths)

        if is_health_check:
            # For health checks, just add correlation ID without verbose logging
            correlation_id = set_correlation_id()
            try:
                response = await call_next(request)
                response.headers["X-Correlation-ID"] = correlation_id

                # Only log health check failures
                if response.status_code >= 400:
                    logger.warning(
                        "Health check failed",
                        extra={
                            "event": "health_check_failed",
                            "url": str(request.url),
                            "status_code": response.status_code,
                        },
                    )

                return response
            except Exception as e:
                logger.error(
                    "Health check error",
                    extra={
                        "event": "health_check_error",
                        "url": str(request.url),
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                    exc_info=True,
                )
                raise
            finally:
                clear_correlation_id()
        else:
            # For non-health check requests, proceed normally
            return await call_next(request)
