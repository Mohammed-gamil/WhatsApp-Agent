import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.agent.graph import call_model

@pytest.fixture
def mock_config_fallback():
    return {
        "system_prompt": "You are a professional WhatsApp AI Assistant.",
        "llm_providers": [
            {
                "provider": "openrouter",
                "model": "first-model",
                "temperature": 0.0
            },
            {
                "provider": "openai",
                "model": "second-model",
                "temperature": 0.1
            }
        ],
        "tools_enabled": {
            "send_whatsapp_text": True
        }
    }

def test_call_model_falls_back_on_failure(mock_config_fallback):
    with patch("app.agent.graph.ConfigService") as mock_config_service_cls, \
         patch("app.agent.graph.ChatOpenAI") as mock_chat_openai_cls:
        
        # Setup mock config service
        mock_service_instance = mock_config_service_cls.return_value
        mock_service_instance.get_config.return_value = mock_config_fallback
        
        # Setup mock model behavior
        # First call to ChatOpenAI (first provider) will return a mock that fails
        # Second call to ChatOpenAI (second provider) will return a mock that succeeds
        
        mock_model_fail = MagicMock()
        mock_model_fail.bind_tools.return_value = mock_model_fail
        mock_model_fail.invoke.side_effect = Exception("Provider failed")
        
        mock_model_success = MagicMock()
        mock_model_success.bind_tools.return_value = mock_model_success
        mock_model_success.invoke.return_value = AIMessage(content="success response")
        
        mock_chat_openai_cls.side_effect = [mock_model_fail, mock_model_success]
        
        # Define state
        state = {
            "messages": [HumanMessage(content="hello")],
            "sender_phone": "12345"
        }
        
        # Call the function
        result = call_model(state)
        
        # Verify fallback occurred
        assert mock_chat_openai_cls.call_count == 2
        
        # Verify first call was for openrouter
        first_call_args = mock_chat_openai_cls.call_args_list[0]
        assert first_call_args.kwargs["model"] == "first-model"
        assert first_call_args.kwargs["openai_api_base"] == "https://openrouter.ai/api/v1"
        
        # Verify second call was for openai
        second_call_args = mock_chat_openai_cls.call_args_list[1]
        assert second_call_args.kwargs["model"] == "second-model"
        assert second_call_args.kwargs["openai_api_base"] is None or second_call_args.kwargs["openai_api_base"] == "" # Depending on implementation
        
        # Verify result is from second provider
        assert result["messages"][0].content == "success response"

def test_call_model_all_providers_fail(mock_config_fallback):
    with patch("app.agent.graph.ConfigService") as mock_config_service_cls, \
         patch("app.agent.graph.ChatOpenAI") as mock_chat_openai_cls:
        
        # Setup mock config service
        mock_service_instance = mock_config_service_cls.return_value
        mock_service_instance.get_config.return_value = mock_config_fallback
        
        # Setup mock model behavior: both fail
        mock_model_fail = MagicMock()
        mock_model_fail.bind_tools.return_value = mock_model_fail
        mock_model_fail.invoke.side_effect = Exception("Provider failed")
        
        mock_chat_openai_cls.return_value = mock_model_fail
        
        # Define state
        state = {
            "messages": [HumanMessage(content="hello")],
            "sender_phone": "12345"
        }
        
        # Call the function
        result = call_model(state)
        
        # Verify all tried
        assert mock_chat_openai_cls.call_count == 2
        
        # Verify result is a helpful error message
        assert isinstance(result["messages"][0], AIMessage)
        assert "trouble connecting" in result["messages"][0].content
