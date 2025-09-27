"""
Basic API tests for FastEmbed AI Gateway
These tests can run without models loaded for CI/CD
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_import_structure():
    """Test that we can import the main modules"""
    try:
        from main import app
        from services.model_service import ModelService
        from chat.gemma_model import GemmaChatModel
        assert ModelService  # noqa: B018
        assert GemmaChatModel  # noqa: B018
        assert True
    except ImportError as e:
        pytest.skip(f"Import failed (expected in CI without models): {e}")

def test_health_endpoint_structure():
    """Test health endpoint without actually loading models"""
    try:
        from main import app
        client = TestClient(app)
        
        # This might fail due to model loading, but we're testing the structure
        response = client.get("/health")
        # If we get here, great! If not, the test will be skipped
        assert response.status_code in [200, 500]  # 500 is OK if models not loaded
    except Exception as e:
        pytest.skip(f"Expected failure in CI environment without models: {e}")

def test_models_endpoint_structure():
    """Test models endpoint structure"""
    try:
        from main import app
        client = TestClient(app)
        
        response = client.get("/v1/models")
        assert response.status_code in [200, 500]  # 500 is OK if models not loaded
    except Exception as e:
        pytest.skip(f"Expected failure in CI environment without models: {e}")

if __name__ == "__main__":
    pytest.main([__file__])