# Dynamic Configuration System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a dynamic configuration system that allows real-time updates to the agent's system prompt, LLM settings, and enabled tools via the Streamlit UI.

**Architecture:** A JSON-based configuration file (`data/agent_config.json`) managed by a `ConfigService`. The LangGraph agent will pull this configuration on every request to determine its behavior and available tools.

**Tech Stack:** FastAPI, LangGraph, Pydantic, Streamlit.

---

### Task 1: Configuration Service & Storage

**Files:**
- Create: `app/services/config_service.py`
- Create: `data/agent_config.json`
- Test: `tests/test_config_service.py`

- [ ] **Step 1: Create initial data directory and default config**

```python
import os
import json

def create_default_config():
    os.makedirs("data", exist_ok=True)
    config_path = "data/agent_config.json"
    if not os.path.exists(config_path):
        default_config = {
            "system_prompt": "You are a professional WhatsApp AI Assistant. You MUST ALWAYS use the 'send_whatsapp_text' tool to send your reply to the user. Never just type a message in plain text; if you do, the user will never see it.",
            "llm": {
                "provider": "openrouter",
                "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
                "temperature": 0.0
            },
            "tools_enabled": {
                "send_whatsapp_text": True,
                "send_whatsapp_image": True,
                "send_whatsapp_document": True,
                "launch_whatsapp_campaign": True
            },
            "rag": {
                "enabled": False,
                "backend_url": ""
            }
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)

create_default_config()
```

- [ ] **Step 2: Implement ConfigService**

```python
import json
import os
from loguru import logger

CONFIG_PATH = "data/agent_config.json"

class ConfigService:
    @staticmethod
    def get_config() -> dict:
        if not os.path.exists(CONFIG_PATH):
            return {}
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading config: {e}")
            return {}

    @staticmethod
    def update_config(new_config: dict) -> bool:
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(new_config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return False
```

- [ ] **Step 3: Write test for ConfigService**

```python
from app.services.config_service import ConfigService
import os
import json

def test_config_service_read_write():
    test_config = {"test": "value"}
    ConfigService.update_config(test_config)
    read_config = ConfigService.get_config()
    assert read_config == test_config
```

- [ ] **Step 4: Commit**

```bash
git add app/services/config_service.py tests/test_config_service.py
git commit -m "feat: add ConfigService and default agent_config.json"
```

---

### Task 2: FastAPI Configuration Endpoints

**Files:**
- Modify: `app/main.py`
- Test: `tests/test_config_api.py`

- [ ] **Step 1: Add GET and POST endpoints for config**

```python
from app.services.config_service import ConfigService

# Inside create_app()
@app.get("/api/v1/config")
async def get_agent_config():
    return ConfigService.get_config()

@app.post("/api/v1/config")
async def update_agent_config(config: dict):
    success = ConfigService.update_config(config)
    if success:
        return {"status": "success"}
    return {"status": "error", "message": "Failed to update config"}
```

- [ ] **Step 2: Write API test**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_config_api():
    # Test GET
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    
    # Test POST
    new_config = response.json()
    new_config["llm"]["temperature"] = 0.5
    post_res = client.post("/api/v1/config", json=new_config)
    assert post_res.status_code == 200
    
    # Verify change
    verify_res = client.get("/api/v1/config")
    assert verify_res.json()["llm"]["temperature"] == 0.5
```

- [ ] **Step 3: Commit**

```bash
git add app/main.py tests/test_config_api.py
git commit -m "feat: add FastAPI endpoints for dynamic configuration"
```

---

### Task 3: Dynamic LangGraph Agent

**Files:**
- Modify: `app/agent/graph.py`

- [ ] **Step 1: Refactor call_model to use ConfigService**
We will remove the top-level `model` binding and do it inside the node for true dynamism.

```python
from app.services.config_service import ConfigService
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

# Remove the global model and tools binding if they were top-level
# available_tools = [send_whatsapp_text, ...]

def call_model(state: AgentState):
    sender_phone = state["sender_phone"]
    messages = list(state["messages"])
    
    # 1. Load latest config
    config = ConfigService.get_config()
    sys_prompt_text = config.get("system_prompt", "You are a helpful assistant.")
    llm_settings = config.get("llm", {})
    tools_enabled = config.get("tools_enabled", {})
    
    # 2. Filter tools
    all_tools_map = {
        "send_whatsapp_text": send_whatsapp_text,
        "send_whatsapp_image": send_whatsapp_image,
        "send_whatsapp_document": send_whatsapp_document,
        "launch_whatsapp_campaign": launch_whatsapp_campaign
    }
    enabled_tools = [all_tools_map[name] for name, enabled in tools_enabled.items() if enabled and name in all_tools_map]
    
    # 3. Initialize model dynamically
    dynamic_model = ChatOpenAI(
        model=llm_settings.get("model", settings.llm_model),
        temperature=llm_settings.get("temperature", 0),
        openai_api_key=settings.openrouter_api_key or settings.openai_api_key,
        openai_api_base="https://openrouter.ai/api/v1"
    ).bind_tools(enabled_tools)

    # 4. Prepare messages
    system_msg = SystemMessage(content=sys_prompt_text + f"\n\nYou are talking to: {sender_phone}")
    full_messages = [system_msg] + messages

    logger.info(f"Invoking dynamic LLM ({llm_settings.get('model')}) for {sender_phone}...")
    response = dynamic_model.invoke(full_messages)
    return {"messages": [response]}
```

- [ ] **Step 2: Commit**

```bash
git add app/agent/graph.py
git commit -m "feat: refactor agent graph to use dynamic configuration and tool binding"
```

---

### Task 4: Streamlit Admin Settings Tab

**Files:**
- Modify: `ui_app.py`

- [ ] **Step 1: Add the Settings tab and UI components**

```python
# Add tab4 to tabs list
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Simulator", "📢 Campaign Manager", "⚙️ Logs", "⚙️ Settings"])

with tab4:
    st.header("Agent Configuration")
    
    # Fetch current config
    try:
        config_res = requests.get("http://localhost:8080/api/v1/config")
        if config_res.status_code == 200:
            config = config_res.json()
            
            # 1. LLM Settings
            st.subheader("LLM Settings")
            provider = st.selectbox("Provider", ["openrouter", "openai", "groq"], index=0)
            model_name = st.text_input("Model Name", value=config["llm"]["model"])
            temp = st.slider("Temperature", 0.0, 1.0, float(config["llm"]["temperature"]), 0.1)
            
            # 2. System Prompt
            st.subheader("System Prompt")
            prompt = st.text_area("Base Instructions", value=config["system_prompt"], height=200)
            
            # 3. Tools Toggles
            st.subheader("Enabled Tools")
            t_text = st.checkbox("Text Messaging", value=config["tools_enabled"]["send_whatsapp_text"])
            t_image = st.checkbox("Image Support", value=config["tools_enabled"]["send_whatsapp_image"])
            t_doc = st.checkbox("Document Support", value=config["tools_enabled"]["send_whatsapp_document"])
            t_camp = st.checkbox("Campaign Management", value=config["tools_enabled"]["launch_whatsapp_campaign"])
            
            if st.button("Save Settings"):
                updated_config = {
                    "system_prompt": prompt,
                    "llm": {"provider": provider, "model": model_name, "temperature": temp},
                    "tools_enabled": {
                        "send_whatsapp_text": t_text,
                        "send_whatsapp_image": t_image,
                        "send_whatsapp_document": t_doc,
                        "launch_whatsapp_campaign": t_camp
                    },
                    "rag": config.get("rag", {"enabled": False, "backend_url": ""})
                }
                save_res = requests.post("http://localhost:8080/api/v1/config", json=updated_config)
                if save_res.status_code == 200:
                    st.success("Configuration updated successfully!")
                else:
                    st.error("Failed to update configuration.")
        else:
            st.error("Could not fetch configuration from backend.")
    except Exception as e:
        st.error(f"Connection Error: {e}")
```

- [ ] **Step 2: Commit**

```bash
git add ui_app.py
git commit -m "feat: add Settings tab to Streamlit UI for dynamic configuration"
```

---

### Task 5: Final Verification

- [ ] **Step 1: Start everything**
Run `python tunnel_manager.py` (which starts FastAPI) and `streamlit run ui_app.py`.

- [ ] **Step 2: Change prompt and test**
Go to Settings, change the prompt to "You are a pirate", save, and send a message. Verify the agent speaks like a pirate.

- [ ] **Step 3: Disable tool and test**
Disable "Image Support", save, and ask for a picture. Verify the agent says it can't or doesn't use the tool.
