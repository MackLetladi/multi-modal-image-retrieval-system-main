import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from pathlib import Path
import os
import shutil
from PIL import Image
import sys

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.src.api.main import app, SearchQuery, RateLimiter, ConnectionManager
from backend.src.config import DATA_DIR, API_HOST, API_PORT

# Test client with correct base URL
client = TestClient(app, base_url=f"http://{API_HOST}:{API_PORT}")

# ============= Fixtures =============
@pytest.fixture(scope="session")
def test_images_dir():
    """Create temporary test images."""
    test_dir = DATA_DIR / "images"
    test_dir.mkdir(parents=True, exist_ok=True)

    # Create some test images
    for i in range(5):
        img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(test_dir / f"test_image_{i}.jpg")

    yield test_dir

    # Cleanup
    shutil.rmtree(test_dir)

@pytest.fixture(autouse=True)
async def setup_test_environment(monkeypatch):
    """Setup test environment with mocked dependencies."""
    # Mock MultiModalRetrieval
    mock_model = MagicMock()
    mock_model.build_index.return_value = None
    mock_model.search.return_value = [
        ("test_image_1.jpg", 0.8),
        ("test_image_2.jpg", 0.6)
    ]

    # Mock ImageDataset
    mock_dataset = MagicMock()
    mock_dataset.__len__.return_value = 5

    # Patch the dependencies
    with patch("backend.src.api.main.MultiModalRetrieval", return_value=mock_model), \
         patch("backend.src.api.main.ImageDataset", return_value=mock_dataset):

        # Clear any existing app state
        if hasattr(app.state, "retrieval_model"):
            delattr(app.state, "retrieval_model")
        if hasattr(app.state, "dataset"):
            delattr(app.state, "dataset")

        # Initialize app state
        app.state.retrieval_model = mock_model
        app.state.dataset = mock_dataset

        # Trigger startup event
        await app.router.startup()

        yield

        # Cleanup
        await app.router.shutdown()

@pytest.fixture
def mock_retrieval_model():
    """Mock for the MultiModalRetrieval model."""
    mock = MagicMock()
    mock.search.return_value = [("test_image_1.jpg", 0.8), ("test_image_2.jpg", 0.6)]
    return mock

@pytest.fixture
def mock_dataset():
    """Mock for the ImageDataset."""
    mock = MagicMock()
    mock.__len__.return_value = 5
    return mock

# ============= Unit Tests =============
class TestRateLimiter:
    """Unit tests for the RateLimiter class."""

    def test_rate_limiter_init(self):
        limiter = RateLimiter(requests_per_minute=60)
        assert limiter.requests_per_minute == 60
        assert limiter.requests == []

    def test_rate_limiter_allowed(self):
        limiter = RateLimiter(requests_per_minute=2)
        assert limiter.is_allowed() is True
        assert limiter.is_allowed() is True
        assert limiter.is_allowed() is False

class TestSearchQuery:
    """Unit tests for the SearchQuery model."""

    def test_valid_search_query(self):
        query = SearchQuery(query="test query", top_k=5)
        assert query.query == "test query"
        assert query.top_k == 5

    def test_invalid_search_query(self):
        with pytest.raises(ValueError):
            SearchQuery(query="", top_k=5)
        with pytest.raises(ValueError):
            SearchQuery(query="test", top_k=0)
        with pytest.raises(ValueError):
            SearchQuery(query="test", top_k=21)

class TestConnectionManager:
    """Unit tests for the WebSocket ConnectionManager."""

    def test_connection_manager_init(self):
        manager = ConnectionManager()
        assert manager.active_connections == {}

    @pytest.mark.asyncio
    async def test_connection_operations(self):
        manager = ConnectionManager()
        mock_websocket = Mock()

        # Test connect
        await manager.connect(mock_websocket, "test_client")
        assert "test_client" in manager.active_connections

        # Test disconnect
        await manager.disconnect("test_client")
        assert "test_client" not in manager.active_connections

# ============= Integration Tests =============
class TestAPIEndpoints:
    """Integration tests for API endpoints."""

    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model" in data
        assert "device" in data
        assert "dataset_size" in data

    def test_search_endpoint(self, test_images_dir):
        """Test the search endpoint with actual image processing."""
        os.environ["IMAGE_DATA_DIR"] = str(test_images_dir)

        # Test valid search
        response = client.post(
            "/search",
            json={"query": "a test image", "top_k": 3}
        )
        assert response.status_code == 200
        results = response.json()
        assert len(results) <= 3
        assert all(isinstance(r["url"], str) for r in results)
        assert all(0 <= r["score"] <= 1 for r in results)

    def test_static_file_serving(self, test_images_dir):
        """Test static file serving integration."""
        # Create a test image
        img_path = test_images_dir / "test_image.jpg"
        img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(img_path)

        # Mount static files
        app.mount("/images", StaticFiles(directory=str(test_images_dir)), name="images")

        response = client.get("/images/test_image.jpg")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/")

class TestErrorHandling:
    """Integration tests for error handling."""

    def test_invalid_endpoint(self):
        response = client.get("/invalid")
        assert response.status_code == 404

    def test_invalid_method(self):
        response = client.put("/search")
        assert response.status_code == 405

    def test_invalid_request_body(self):
        response = client.post(
            "/search",
            json={"invalid": "data"}
        )
        assert response.status_code == 422

class TestMiddleware:
    """Integration tests for middleware components."""

    def test_cors_headers(self):
        """Test CORS headers are properly set."""
        response = client.options(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers.keys()

    def test_security_headers(self):
        """Test security headers are properly set."""
        response = client.get("/health")
        assert "content-security-policy" in response.headers
        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers

    def test_rate_limiting(self):
        """Test rate limiting middleware."""
        responses = []
        for _ in range(70):  # More than the rate limit
            response = client.get("/health")
            responses.append(response.status_code)

        assert 429 in responses  # Should see some rate limit responses
