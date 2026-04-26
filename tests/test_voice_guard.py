# tests/test_voice_guard.py
from src.agent.voice_guard import build_system_prompt, filter_forbidden_phrases

def test_build_system_prompt():
    prompt = build_system_prompt()
    assert "Amplify your expertise" in prompt
    # Check that it's mentioned as a negative constraint
    assert "NEVER use" in prompt and "AI-powered solutions" in prompt

def test_filter_forbidden_phrases():
    bad_text = "We offer AI-powered solutions with cutting-edge technology."
    clean_text = filter_forbidden_phrases(bad_text)
    assert "AI-powered solutions" not in clean_text
    assert "cutting-edge technology" not in clean_text
    assert "Amplify your expertise" in clean_text
