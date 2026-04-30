from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

client = TestClient(app)

def test_handle_whats360_webhook_success():
    payload = {
        "event": "message.received",
        "data": {
            "from": "1234567890",
            "text": "Hello agent"
        }
    }
    with patch("src.api.whatsapp.run_whatsapp_agent") as mock_run:
        response = client.post("/webhook/whats360", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"status": "success", "message": "Agent triggered in background"}
        mock_run.assert_called_once_with("1234567890", "Hello agent")

def test_handle_whats360_webhook_ignore_status():
    payload = {
        "event": "message.status",
        "data": {
            "id": "msg_123",
            "status": "delivered"
        }
    }
    response = client.post("/webhook/whats360", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ignored", "event": "message.status"}

def test_handle_whats360_webhook_missing_data():
    payload = {
        "event": "message.received",
        "data": {
            "from": "1234567890"
            # text missing
        }
    }
    response = client.post("/webhook/whats360", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ignored", "reason": "Missing from or text in message data"}
