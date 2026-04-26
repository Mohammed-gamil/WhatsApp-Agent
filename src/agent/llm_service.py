from litellm import completion

def generate_response(prompt: str, provider: str = "openai") -> str:
    # provider format expected by litellm: "openai/gpt-4", "groq/llama3-8b-8192", "openrouter/anthropic/claude-3-opus"
    model_name = f"{provider}/default-model" if "/" not in provider else provider
    
    response = completion(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]
