# Prioritized LLM Fallback System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a prioritized (tiered) fallback mechanism for LLM providers to ensure agent availability.

**Architecture:** Update the configuration schema to support a list of providers and refactor the LangGraph agent to loop through them upon failure. Update the UI to manage this list.

**Tech Stack:** FastAPI, LangGraph, Streamlit.

---

### Task 1: Update Configuration Schema & Defaults

**Files:**
- Modify: `app/services/config_service.py`
- Modify: `data/agent_config.json`

- [ ] **Step 1: Update `create_default_config` in `app/services/config_service.py`**
Replace the single `llm` object with `llm_providers` list.

```python
# In create_default_config()
default_config = {
    "system_prompt": "...",
    "llm_providers": [
        {
            "provider": "openrouter",
            "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            "temperature": 0.0
        }
    ],
    # ... rest
}
```

- [ ] **Step 2: Update existing `data/agent_config.json`**
Manually or programmatically migrate the existing file to the new structure.

- [ ] **Step 3: Commit**
```bash
git add app/services/config_service.py data/agent_config.json
git commit -m "refactor: update config schema for multiple llm providers"
```

---

### Task 2: Implement Fallback Logic in Agent Graph

**Files:**
- Modify: `app/agent/graph.py`

- [ ] **Step 1: Update `call_model` with loop logic**
Wrap the model invocation in a loop that iterates through `llm_providers`.

```python
def call_model(state: AgentState):
    # ... setup ...
    config = ConfigService.get_config()
    providers = config.get("llm_providers", [])
    
    last_error = None
    for p_config in providers:
        try:
            # Initialize model with p_config
            model = ChatOpenAI(
                model=p_config.get("model"),
                temperature=p_config.get("temperature", 0),
                openai_api_key=get_api_key(p_config.get("provider")),
                openai_api_base=get_base_url(p_config.get("provider"))
            ).bind_tools(enabled_tools)
            
            response = model.invoke(full_messages)
            return {"messages": [response]}
        except Exception as e:
            logger.warning(f"Provider {p_config.get('provider')} failed: {e}")
            last_error = e
            continue
            
    # If all fail
    error_msg = AIMessage(content="I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment.")
    return {"messages": [error_msg]}
```

- [ ] **Step 2: Commit**
```bash
git add app/agent/graph.py
git commit -m "feat: implement prioritized fallback logic in agent graph"
```

---

### Task 3: Update Admin UI for Multiple Providers

**Files:**
- Modify: `ui_app.py`

- [ ] **Step 1: Update Settings tab to manage providers list**
Add UI components to add, remove, and list providers.

```python
# In tab4 (Settings)
st.subheader("LLM Providers (Priority Order)")
for i, p in enumerate(config["llm_providers"]):
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    col1.write(f"**{p['provider']}**: {p['model']}")
    if col3.button("Remove", key=f"rm_{i}"):
        config["llm_providers"].pop(i)
        save_config(config)
        st.rerun()
        
# Add new provider form
with st.expander("Add Fallback Provider"):
    # ... inputs ...
    if st.button("Add"):
        config["llm_providers"].append(new_p)
        save_config(config)
        st.rerun()
```

- [ ] **Step 2: Commit**
```bash
git add ui_app.py
git commit -m "feat: update UI to manage multiple LLM providers"
```

---

### Task 4: Final Verification

- [ ] **Step 1: Test with invalid primary**
Set an invalid model name for the first provider and verify it falls back to the second.
- [ ] **Step 2: Verify UI persistence**
Add a provider in UI, refresh, and check if it's still there.
- [ ] **Step 3: Commit**
```bash
git commit -m "test: verify llm fallback system"
```
