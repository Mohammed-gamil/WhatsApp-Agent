# tests/test_llm_service.py
from src.agent.llm_service import generate_response

def test_generate_response(mocker):
    # Mock liteLLM completion to avoid actual API calls
    mocker.patch("src.agent.llm_service.completion", return_value={"choices": [{"message": {"content": "Hello"}}]})
    result = generate_response("Hi", provider="fake_provider")
    assert result == "Hello"
