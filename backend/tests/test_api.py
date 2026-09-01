"""Smoke tests for the FastAPI backend."""

import pytest
from fastapi.testclient import TestClient


def test_health_check():
    """The health endpoint should return 200 and a healthy status."""
    from app.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")


def test_root_endpoint():
    """The root endpoint should return service information."""
    from app.main import app
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
