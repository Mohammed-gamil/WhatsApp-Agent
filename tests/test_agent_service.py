import pytest
from unittest.mock import MagicMock, patch
from src.agent.service import run_whatsapp_agent

@patch("src.agent.service.create_agent")
@patch("src.agent.service.get_settings")
def test_run_whatsapp_agent_calls_agent_invoke(mock_get_settings, mock_create_agent):
    # Setup mocks
    mock_settings = MagicMock()
    mock_settings.openai_api_key = "test_key"
    mock_get_settings.return_value = mock_settings
    
    mock_agent = MagicMock()
    mock_create_agent.return_value = mock_agent
    
    sender_phone = "1234567890"
    user_message = "Hello agent"
    
    # Run the function
    run_whatsapp_agent(sender_phone, user_message)
    
    # Verify expectations
    mock_create_agent.assert_called_once()
    mock_agent.invoke.assert_called_once()
    
    # Check if create_agent was called with correct system prompt
    _, kwargs = mock_create_agent.call_args
    system_prompt = kwargs.get("system_prompt", "")
    assert sender_phone in system_prompt
    assert "whatsapp_sender" in system_prompt
    
    # Check if agent.invoke was called with correct message
    args, _ = mock_agent.invoke.call_args
    state = args[0]
    assert state["messages"][0][1] == user_message
