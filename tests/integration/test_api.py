"""Integration tests for API."""

import pytest
from fastapi.testclient import TestClient

from lambdax.api.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_inspect_clean_input(client):
    """Test inspection of clean input."""
    response = client.post(
        "/v1/inspect",
        json={
            "text": "Hello, how can I help you?",
            "direction": "input",
            "policy_id": "default",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["blocked"] is False
    assert "request_id" in data


def test_inspect_with_email(client):
    """Test inspection of input with email."""
    response = client.post(
        "/v1/inspect",
        json={
            "text": "Contact me at user@example.com",
            "direction": "input",
            "policy_id": "default",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["blocked"] is True
    assert "EMAIL" in data["reason"]


def test_inspect_invalid_direction(client):
    """Test inspection with invalid direction."""
    response = client.post(
        "/v1/inspect",
        json={
            "text": "Test",
            "direction": "invalid",
            "policy_id": "default",
        },
    )

    assert response.status_code == 400


def test_clear_cache(client):
    """Test cache clearing endpoint."""
    response = client.post("/v1/clear-cache")
    assert response.status_code == 200
    assert response.json()["status"] == "cache cleared"


def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
