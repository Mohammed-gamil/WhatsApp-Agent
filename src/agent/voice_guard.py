FORBIDDEN_MAPPING = {
    "AI-powered solutions": "Amplify your expertise",
    "Cutting-edge technology": "Expand what your team can do",
    "ai-powered solutions": "amplify your expertise",
    "cutting-edge technology": "expand what your team can do"
}

def build_system_prompt() -> str:
    return """You are an expert outbound sales consultant. 
Your communication style must strictly adhere to our marketing profile:
- NEVER use phrases like 'AI-powered solutions' or 'cutting-edge technology'.
- ALWAYS focus on human empowerment. Use phrases like 'Amplify your expertise' and 'Expand what your team can do'.
Be professional, direct, and focused on tangible value."""

def filter_forbidden_phrases(text: str) -> str:
    # Simple replacement as a fail-safe
    filtered_text = text
    for bad, good in FORBIDDEN_MAPPING.items():
        filtered_text = filtered_text.replace(bad, good)
    return filtered_text
