from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
import pytest

# Mock the agent_app globally for these tests
@pytest.fixture(autouse=True)
def mock_agent_app():
    with patch("app.api.webhook.agent_app") as mock:
        mock.ainvoke = AsyncMock(return_value={"messages": []})
        yield mock

client = TestClient(app)

def test_receive_whats360_webhook_success(mock_agent_app):
    payload = {
        "event": "message.received",
        "data": {
            "from": "201097294152",
            "text": "Hello agent",
            "message_id": "msg_123"
        }
    }
    
    response = client.post("/api/v1/webhook/whats360", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

def test_receive_whats360_webhook_duplicate():
    payload = {
        "event": "message.received",
        "data": {
            "from": "201097294152",
            "text": "Hello again",
            "message_id": "msg_unique_123"
        }
    }
    
    # First call
    response = client.post("/api/v1/webhook/whats360", json=payload)
    assert response.status_code == 200
    
    # Second call with same message_id
    response = client.post("/api/v1/webhook/whats360", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Duplicate ignored"}

def test_receive_whats360_webhook_ignore_event():
    payload = {
        "event": "message.status",
        "data": {
            "status": "delivered",
            "message_id": "msg_123"
        }
    }
    response = client.post("/api/v1/webhook/whats360", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ignored", "event": "message.status"}
