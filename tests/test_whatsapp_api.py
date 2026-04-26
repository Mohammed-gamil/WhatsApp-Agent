# tests/test_whatsapp_api.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_verify_webhook():
    response = client.get("/webhook?hub.mode=subscribe&hub.verify_token=test_token&hub.challenge=1234")
    assert response.status_code == 200
    assert response.text == "1234"
