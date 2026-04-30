import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import json

client = TestClient(app)

def test_config_api_endpoints():
    # 1. Test GET /api/v1/config
    response = client.get("/api/v1/config")
    # This should fail initially (404)
    assert response.status_code == 200
    config = response.json()
    assert "system_prompt" in config
    assert "llm_providers" in config
    
    # 2. Test POST /api/v1/config
    original_temp = config["llm_providers"][0]["temperature"]
    new_temp = 0.7 if original_temp == 0.0 else 0.0
    config["llm_providers"][0]["temperature"] = new_temp
    
    post_response = client.post("/api/v1/config", json=config)
    assert post_response.status_code == 200
    assert post_response.json()["status"] == "success"
    
    # 3. Verify change with GET
    verify_response = client.get("/api/v1/config")
    assert verify_response.status_code == 200
    assert verify_response.json()["llm_providers"][0]["temperature"] == new_temp
