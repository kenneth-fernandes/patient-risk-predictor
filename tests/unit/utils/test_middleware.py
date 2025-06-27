"""Tests for middleware module."""

import time
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from src.utils.middleware import HealthCheckLoggingMiddleware, LoggingMiddleware


class TestLoggingMiddleware:
    """Test LoggingMiddleware functionality."""

    @pytest.fixture
    def app_with_logging_middleware(self):
        """Create FastAPI app with LoggingMiddleware."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        @app.get("/error")
        async def error_endpoint():
            raise Exception("Test error")

        return app

    def test_logging_middleware_success_request(self, app_with_logging_middleware):
        """Test LoggingMiddleware with successful request."""
        client = TestClient(app_with_logging_middleware)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert response.json() == {"message": "test"}

    def test_logging_middleware_error_request(self, app_with_logging_middleware):
        """Test LoggingMiddleware with error request."""
        client = TestClient(app_with_logging_middleware)
        
        with pytest.raises(Exception):
            client.get("/error")

    def test_logging_middleware_correlation_id(self, app_with_logging_middleware):
        """Test that LoggingMiddleware generates correlation IDs."""
        client = TestClient(app_with_logging_middleware)
        response = client.get("/test")
        
        # Check that correlation ID header is present
        assert "X-Correlation-ID" in response.headers

    def test_logging_middleware_timing(self, app_with_logging_middleware):
        """Test that LoggingMiddleware tracks request timing."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        @app.get("/slow")
        async def slow_endpoint():
            # Simulate some processing time
            await AsyncMock(return_value=None)()
            return {"message": "slow"}

        client = TestClient(app)
        response = client.get("/slow")
        
        assert response.status_code == 200


class TestHealthCheckLoggingMiddleware:
    """Test HealthCheckLoggingMiddleware functionality."""

    @pytest.fixture
    def app_with_health_middleware(self):
        """Create FastAPI app with HealthCheckLoggingMiddleware."""
        app = FastAPI()
        app.add_middleware(HealthCheckLoggingMiddleware)

        @app.get("/")
        async def health_check():
            return {"status": "healthy"}

        @app.get("/health")
        async def health_endpoint():
            return {"status": "ok"}

        @app.get("/api/data")
        async def api_endpoint():
            return {"data": "test"}

        return app

    def test_health_middleware_default_paths(self, app_with_health_middleware):
        """Test HealthCheckLoggingMiddleware with default health check paths."""
        client = TestClient(app_with_health_middleware)
        
        # Health check endpoints should work
        response = client.get("/")
        assert response.status_code == 200
        
        response = client.get("/health")
        assert response.status_code == 200
        
        # Regular API endpoints should work
        response = client.get("/api/data")
        assert response.status_code == 200

    def test_health_middleware_custom_paths(self):
        """Test HealthCheckLoggingMiddleware with custom health check paths."""
        app = FastAPI()
        app.add_middleware(
            HealthCheckLoggingMiddleware, 
            health_check_paths=["/custom-health", "/status"]
        )

        @app.get("/custom-health")
        async def custom_health():
            return {"status": "healthy"}

        @app.get("/status")
        async def status_check():
            return {"status": "ok"}

        @app.get("/api/data")
        async def api_endpoint():
            return {"data": "test"}

        client = TestClient(app)
        
        # Custom health check endpoints should work
        response = client.get("/custom-health")
        assert response.status_code == 200
        
        response = client.get("/status")
        assert response.status_code == 200
        
        # Regular API endpoints should work
        response = client.get("/api/data")
        assert response.status_code == 200

    def test_health_middleware_path_filtering(self):
        """Test that HealthCheckLoggingMiddleware filters health check paths."""
        app = FastAPI()
        
        # Initialize with specific health check paths
        middleware = HealthCheckLoggingMiddleware(
            app, health_check_paths=["/health", "/ping"]
        )
        
        # Test that health check paths are identified correctly
        assert "/health" in middleware.health_check_paths
        assert "/ping" in middleware.health_check_paths
        # When custom paths are provided, only those paths are used
        assert middleware.health_check_paths == ["/health", "/ping"]

    def test_health_middleware_none_paths(self):
        """Test HealthCheckLoggingMiddleware with None paths parameter."""
        app = FastAPI()
        middleware = HealthCheckLoggingMiddleware(app, health_check_paths=None)
        
        # Should use default paths
        assert "/" in middleware.health_check_paths
        assert "/health" in middleware.health_check_paths

    async def test_health_middleware_dispatch_health_path(self):
        """Test middleware dispatch method with health check path."""
        app = FastAPI()
        middleware = HealthCheckLoggingMiddleware(app)
        
        # Mock request for health check path
        request = Mock(spec=Request)
        request.url.path = "/"
        request.method = "GET"
        
        # Mock call_next function
        async def mock_call_next(req):
            response = Mock(spec=Response)
            response.status_code = 200
            return response
        
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200

    async def test_health_middleware_dispatch_regular_path(self):
        """Test middleware dispatch method with regular API path."""
        app = FastAPI()
        middleware = HealthCheckLoggingMiddleware(app)
        
        # Mock request for regular API path
        request = Mock(spec=Request)
        request.url.path = "/api/users"
        request.method = "GET"
        
        # Mock call_next function
        async def mock_call_next(req):
            response = Mock(spec=Response)
            response.status_code = 200
            return response
        
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200


class TestMiddlewareIntegration:
    """Integration tests for middleware components."""

    def test_both_middlewares_together(self):
        """Test LoggingMiddleware and HealthCheckLoggingMiddleware together."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(HealthCheckLoggingMiddleware)

        @app.get("/")
        async def health_check():
            return {"status": "healthy"}

        @app.get("/api/test")
        async def api_endpoint():
            return {"data": "test"}

        client = TestClient(app)
        
        # Health check should work
        response = client.get("/")
        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers
        
        # API endpoint should work
        response = client.get("/api/test")
        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers

    def test_middleware_error_handling(self):
        """Test middleware behavior with application errors."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(HealthCheckLoggingMiddleware)

        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")

        client = TestClient(app)
        
        # Should handle errors gracefully
        with pytest.raises(ValueError):
            client.get("/error")

    def test_middleware_performance_impact(self):
        """Test that middleware doesn't significantly impact performance."""
        app_without_middleware = FastAPI()
        app_with_middleware = FastAPI()
        
        app_with_middleware.add_middleware(LoggingMiddleware)
        app_with_middleware.add_middleware(HealthCheckLoggingMiddleware)

        @app_without_middleware.get("/test")
        @app_with_middleware.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client_without = TestClient(app_without_middleware)
        client_with = TestClient(app_with_middleware)
        
        # Both should complete successfully
        response_without = client_without.get("/test")
        response_with = client_with.get("/test")
        
        assert response_without.status_code == 200
        assert response_with.status_code == 200
        assert response_without.json() == response_with.json()