"""
Unit tests for health_controller
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.adapters.input.routers.health_controller import router


@pytest.fixture
def test_app():
    """Create a test FastAPI app"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(test_app):
    """Create a test client"""
    return TestClient(test_app)


class TestHealthController:
    """Test cases for health controller"""
    
    def test_health_check_endpoint_exists(self, client):
        """Test that health check endpoint exists"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_check_returns_json(self, client):
        """Test that health check returns JSON"""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"
    
    def test_health_check_response_structure(self, client):
        """Test health check response structure"""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "service" in data
    
    def test_health_check_response_values(self, client):
        """Test health check response values"""
        response = client.get("/health")
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "video-processor"
    
    def test_health_check_multiple_calls(self, client):
        """Test multiple health check calls"""
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    
    def test_health_check_method_not_allowed(self, client):
        """Test that POST method is not allowed on health endpoint"""
        response = client.post("/health")
        assert response.status_code == 405
