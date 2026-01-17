"""Integration tests for API."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


class TestChatAPI:
    """Tests for chat API endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    @pytest.mark.skip(reason="Requires LM Studio to be running")
    def test_chat_endpoint(self):
        """Test chat endpoint."""
        response = client.post(
            "/chat/",
            json={"message": "Hello", "metadata": {}},
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert "session_id" in response.json()


class TestPaymentAPI:
    """Tests for payment API endpoints."""

    def test_process_payment(self):
        """Test payment processing."""
        response = client.post(
            "/payment/process",
            json={
                "amount": 100.0,
                "currency": "USD",
                "description": "Test payment",
            },
        )
        assert response.status_code == 200
        assert "transaction_id" in response.json()
        assert "status" in response.json()
