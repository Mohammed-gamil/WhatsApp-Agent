import pytest
from unittest.mock import patch, MagicMock
from src.api.outbound import send_whats360_message

@patch("src.api.outbound.requests.post")
@patch("src.api.outbound.get_settings")
def test_send_whats360_message_success(mock_get_settings, mock_post):
    # Mock settings
    mock_settings = MagicMock()
    mock_settings.whats360_api_url = "https://api.whats360.test"
    mock_settings.whats360_token = "test_token"
    mock_get_settings.return_value = mock_settings
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "id": "msg_123"}
    mock_post.return_value = mock_response
    
    result = send_whats360_message("123456789", "Hello!")
    
    assert result == {"success": True, "id": "msg_123"}
    mock_post.assert_called_once_with(
        "https://api.whats360.test/messages/send",
        json={"to": "123456789", "text": "Hello!"},
        headers={
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json"
        },
        timeout=10
    )

@patch("src.api.outbound.requests.post")
@patch("src.api.outbound.get_settings")
def test_send_whats360_message_failure(mock_get_settings, mock_post):
    # Mock settings
    mock_settings = MagicMock()
    mock_settings.whats360_api_url = "https://api.whats360.test"
    mock_settings.whats360_token = "test_token"
    mock_get_settings.return_value = mock_settings
    
    # Mock post exception
    mock_post.side_effect = Exception("Connection error")
    
    result = send_whats360_message("123456789", "Hello!")
    
    assert result["success"] is False
    assert "Connection error" in result["error"]
