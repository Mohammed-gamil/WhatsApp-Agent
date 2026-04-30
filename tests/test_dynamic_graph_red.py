import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, SystemMessage
import operator

# Mock the ConfigService and ChatOpenAI before importing call_model
# because graph.py might have top-level code that fails if dependencies are missing.

@pytest.fixture
def mock_config():
    return {
        "system_prompt": "DYNAMIC SYSTEM PROMPT",
        "llm": {
            "provider": "openrouter",
            "model": "dynamic-model",
            "temperature": 0.5
        },
        "tools_enabled": {
            "send_whatsapp_text": True,
            "send_whatsapp_image": False,
            "send_whatsapp_document": False,
            "launch_whatsapp_campaign": False
        },
        "rag": {
            "enabled": False,
            "backend_url": ""
        }
    }

def test_call_model_uses_dynamic_config(mock_config):
    # Use patch.dict to mock settings if needed, or just patch ChatOpenAI
    with patch("app.agent.graph.ConfigService") as mock_config_service_cls, \
         patch("app.agent.graph.ChatOpenAI") as mock_chat_openai_cls:
        
        from app.agent.graph import call_model
        
        # Setup mock config service
        mock_service_instance = mock_config_service_cls.return_value
        mock_service_instance.get_config.return_value = mock_config
        
        # Setup mock model
        mock_model_instance = MagicMock()
        mock_chat_openai_cls.return_value = mock_model_instance
        mock_model_instance.bind_tools.return_value = mock_model_instance
        mock_model_instance.invoke.return_value = MagicMock(content="response", tool_calls=[])
        
        # Define state
        state = {
            "messages": [HumanMessage(content="hello")],
            "sender_phone": "12345"
        }
        
        # Call the function
        call_model(state)
        
        # 1. Verify ConfigService was called
        mock_service_instance.get_config.assert_called_once()
        
        # 2. Verify ChatOpenAI was initialized with dynamic config
        # Note: We need to see how it's called.
        mock_chat_openai_cls.assert_called()
        args, kwargs = mock_chat_openai_cls.call_args
        assert kwargs["model"] == "dynamic-model"
        assert kwargs["temperature"] == 0.5
        
        # 3. Verify model.invoke was called with the DYNAMIC SYSTEM PROMPT
        mock_model_instance.invoke.assert_called()
        invoke_args, _ = mock_model_instance.invoke.call_args
        messages = invoke_args[0]
        
        # Check if any message is a SystemMessage with our dynamic prompt
        system_messages = [m for m in messages if isinstance(m, SystemMessage)]
        assert len(system_messages) > 0
        assert "DYNAMIC SYSTEM PROMPT" in system_messages[0].content
        
        # 4. Verify only enabled tools were bound
        mock_model_instance.bind_tools.assert_called_once()
        bound_tools = mock_model_instance.bind_tools.call_args[0][0]
        assert len(bound_tools) == 1
        assert bound_tools[0].name == "send_whatsapp_text"
