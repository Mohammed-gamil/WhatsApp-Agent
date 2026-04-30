# Design Spec: Prioritized LLM Fallback System

**Date:** 2026-04-30
**Topic:** Implementing a tiered fallback mechanism for LLM providers.

## 1. Overview
Ensure the agent remains responsive by automatically switching to backup LLM providers if the primary provider fails (e.g., API downtime, rate limits).

## 2. Configuration Changes (`data/agent_config.json`)
The `llm` key will be replaced by `llm_providers`, which is an ordered list.

```json
{
  "system_prompt": "...",
  "llm_providers": [
    {
      "provider": "openrouter",
      "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
      "temperature": 0.0
    },
    {
      "provider": "openai",
      "model": "gpt-4o-mini",
      "temperature": 0.1
    }
  ],
  "tools_enabled": { ... }
}
```

## 3. Backend Logic (`app/agent/graph.py`)
The `call_model` node will be updated to:
1. Retrieve the `llm_providers` list from the configuration.
2. Iterate through the list in order.
3. For each provider:
    - Initialize the corresponding `ChatOpenAI` instance.
    - Attempt to `invoke()` the model.
    - If successful, log the provider used and return the result.
    - If an exception occurs (e.g., `openai.APIError`, `requests.RequestException`), log a warning and proceed to the next provider.
4. If all providers fail, log a critical error and return a fallback message to the user asking them to try again later.

## 4. Admin UI (`ui_app.py`)
- **Settings Tab:**
    - Replace the single LLM inputs with a list view.
    - Display current providers with "Remove" buttons.
    - Add an "Add New Provider" form (Dropdown for provider, Text for model, Slider for temperature).
    - Provide a way to reorder providers (e.g., up/down buttons).

## 5. Testing
- **Unit Test:** Mock failures for the first provider and verify the second one is called.
- **Manual Test:** Intentionally break the primary provider (e.g., invalid API key) and confirm the agent still responds using the fallback.

## 6. Success Criteria
- The agent successfully falls back to the second provider when the first fails.
- Configuration is correctly persisted and managed via the UI.
- No interruption in service for the end user during a fallback event.
