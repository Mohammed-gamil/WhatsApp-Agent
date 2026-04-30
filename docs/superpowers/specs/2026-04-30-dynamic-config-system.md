# Design Spec: Dynamic Configuration System for WhatsApp Agent

**Date:** 2026-04-30
**Topic:** Making system prompt, LLM settings, and tools fully configurable via UI.

## 1. Overview
The goal is to allow the user to modify the agent's behavior (system prompt, model, tools) dynamically through the Streamlit admin UI without restarting the FastAPI server or editing code.

## 2. Architecture
- **Storage:** A JSON file located at `data/agent_config.json`.
- **Config Service:** A singleton service in the FastAPI app to read/write the JSON.
- **Dynamic Graph:** The LangGraph `call_model` node will retrieve the current configuration on every invocation.
- **Admin UI:** A new "Settings" tab in `ui_app.py` for managing the configuration.

## 3. Data Structure (`data/agent_config.json`)
```json
{
  "system_prompt": "You are a professional WhatsApp AI Assistant...",
  "llm": {
    "provider": "openrouter",
    "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "temperature": 0.0
  },
  "tools_enabled": {
    "send_whatsapp_text": true,
    "send_whatsapp_image": true,
    "send_whatsapp_document": true,
    "launch_whatsapp_campaign": true
  },
  "rag": {
    "enabled": false,
    "backend_url": ""
  }
}
```

## 4. Components

### 4.1 FastAPI Backend
- **`app/services/config_service.py`**:
    - `get_config()`: Loads JSON.
    - `update_config(new_config)`: Saves JSON.
- **`app/main.py`**:
    - Add `POST /api/v1/config` to update settings.
    - Add `GET /api/v1/config` to fetch settings.
- **`app/agent/graph.py`**:
    - The `call_model` node will use `ConfigService.get_config()`.
    - Tools will be dynamically filtered based on `tools_enabled`.
    - The `ChatOpenAI` instance will be configured per-request or re-initialized if settings change.

### 4.2 Streamlit UI (`ui_app.py`)
- Add a `tab4` for "⚙️ Settings".
- Input fields for all JSON properties.
- "Save Configuration" button to send data to the FastAPI endpoint.

## 5. Dynamic Tool Toggling
In `app/agent/graph.py`, instead of binding all tools at the top level, the `call_model` function will:
1. Fetch enabled tools from config.
2. Filter the available tools list.
3. Bind the filtered tools to the model before `model.invoke()`.

## 6. Testing Strategy
- **Unit Test:** Verify `ConfigService` reads/writes correctly.
- **Integration Test:** Verify `POST /api/v1/config` updates the behavior of the next `POST /api/v1/webhook/whats360` call.
- **Manual Test:** Change the system prompt in the UI and confirm the agent's tone changes in WhatsApp.

## 7. Success Criteria
- User can change the system prompt in the UI and see the effect immediately.
- User can disable a tool (e.g., Image) and the AI no longer attempts to use it.
- Settings persist after the server is restarted.
