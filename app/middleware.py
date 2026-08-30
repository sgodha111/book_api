"""Middleware for request logging and rate limiting."""

import json
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging of requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details.

        Args:
            request: HTTP request
            call_next: Next middleware in chain

        Returns:
            HTTP response
        """
        # Record start time
        start_time = time.time()

        # Extract request details
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params) if request.query_params else {}

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Log request
        logger.info(
            json.dumps({
                "event": "request_received",
                "timestamp": datetime.utcnow().isoformat(),
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_ip": client_ip,
            })
        )

        # Call next middleware
        response = await call_next(request)

        # Calculate response time
        response_time = time.time() - start_time

        # Log response
        logger.info(
            json.dumps({
                "event": "response_sent",
                "timestamp": datetime.utcnow().isoformat(),
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "response_time_ms": round(response_time * 1000, 2),
                "client_ip": client_ip,
            })
        )

        # Add response time header
        response.headers["X-Process-Time"] = str(response_time)

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for basic rate limiting (100 requests/minute per IP)."""

    def __init__(self, app, requests_per_minute: int = 100):
        """Initialize rate limiter.

        Args:
            app: FastAPI application
            requests_per_minute: Max requests per minute per IP (default: 100)
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing request.

        Args:
            request: HTTP request
            call_next: Next middleware in chain

        Returns:
            HTTP response or 429 if rate limit exceeded
        """
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)

        # Get current time
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)

        # Clean old requests (older than 1 minute)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > one_minute_ago
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(
                json.dumps({
                    "event": "rate_limit_exceeded",
                    "timestamp": datetime.utcnow().isoformat(),
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "requests_count": len(self.requests[client_ip]),
                })
            )

            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Maximum 100 requests per minute.",
                    "retry_after": 60,
                },
            )

        # Record this request
        self.requests[client_ip].append(now)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.requests[client_ip])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int((now + timedelta(minutes=1)).timestamp())
        )

        return response
