import pytest
from unittest.mock import patch
from src.agent.tools import whatsapp_sender

def test_whatsapp_sender_success():
    with patch("src.agent.tools.send_whats360_message") as mock_send:
        mock_send.return_value = {"success": True, "id": "12345"}
        
        result = whatsapp_sender.run({"to_number": "1234567890", "text": "Hello"})
        
        assert result == "Message sent successfully."
        mock_send.assert_called_once_with("1234567890", "Hello")

def test_whatsapp_sender_failure():
    with patch("src.agent.tools.send_whats360_message") as mock_send:
        mock_send.return_value = {"success": False, "error": "Invalid token"}
        
        result = whatsapp_sender.run({"to_number": "1234567890", "text": "Hello"})
        
        assert "Failed to send message: Invalid token" in result
        mock_send.assert_called_once_with("1234567890", "Hello")

def test_whatsapp_sender_success_with_id():
    with patch("src.agent.tools.send_whats360_message") as mock_send:
        # Some API responses might not have "success": True but have an "id"
        mock_send.return_value = {"id": "msg_98765"}
        
        result = whatsapp_sender.run({"to_number": "1234567890", "text": "Hello"})
        
        assert result == "Message sent successfully."
        mock_send.assert_called_once_with("1234567890", "Hello")
