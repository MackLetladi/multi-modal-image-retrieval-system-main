import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import shutil
from PIL import Image
import numpy as np

from ..src.api.main import app
from ..src.config import DATA_DIR

# Test client
client = TestClient(app)

# Test data setup
@pytest.fixture(scope="session")
def test_images_dir():
    """Create temporary test images."""
    test_dir = DATA_DIR / "test_images"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create some test images
    for i in range(5):
        img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(test_dir / f"test_image_{i}.jpg")
    
    yield test_dir
    
    # Cleanup
    shutil.rmtree(test_dir)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model" in data
    assert "device" in data
    assert "dataset_size" in data

def test_search_endpoint(test_images_dir):
    """Test the search endpoint."""
    # Set the environment variable for test images
    os.environ["IMAGE_DATA_DIR"] = str(test_images_dir)
    
    # Test valid query
    response = client.post(
        "/search",
        json={"query": "a test image", "top_k": 3}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) <= 3
    assert all(isinstance(r["url"], str) for r in results)
    assert all(0 <= r["score"] <= 1 for r in results)
    
    # Test invalid top_k
    response = client.post(
        "/search",
        json={"query": "test", "top_k": 0}
    )
    assert response.status_code == 422
    
    # Test empty query
    response = client.post(
        "/search",
        json={"query": "", "top_k": 5}
    )
    assert response.status_code == 422
    
    # Test very long query
    response = client.post(
        "/search",
        json={"query": "a" * 501, "top_k": 5}
    )
    assert response.status_code == 422

def test_rate_limiting():
    """Test rate limiting middleware."""
    # Make multiple requests quickly
    responses = []
    for _ in range(70):  # More than the rate limit
        response = client.get("/health")
        responses.append(response.status_code)
    
    # Should see some 429 responses
    assert 429 in responses

def test_static_files(test_images_dir):
    """Test static file serving."""
    # Try to access a test image
    test_image = next(test_images_dir.glob("*.jpg"))
    response = client.get(f"/images/{test_image.name}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")

def test_error_handling():
    """Test error handling."""
    # Test invalid endpoint
    response = client.get("/invalid")
    assert response.status_code == 404
    
    # Test invalid method
    response = client.put("/search")
    assert response.status_code == 405
    
    # Test invalid JSON
    response = client.post(
        "/search",
        data="invalid json"
    )
    assert response.status_code == 422
