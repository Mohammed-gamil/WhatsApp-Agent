# WhatsApp AI Agent (Whats360) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-ready WhatsApp AI Agent using the Whats360 unofficial gateway with FastAPI and LangChain.

**Architecture:** A FastAPI webhook receives incoming messages and immediately returns 200 OK. A BackgroundTask then triggers a LangChain ReAct agent which processes the message and autonomously replies using a tool that calls the Whats360 outbound API.

**Tech Stack:** FastAPI, LangChain, OpenAI, Requests, python-dotenv.

---

### Task 1: Environment Configuration

**Files:**
- Modify: `src/config/settings.py`
- Create: `.env` (template)

- [ ] **Step 1: Update Settings model**
Update `Settings` in `src/config/settings.py` to include Whats360 and OpenAI keys.

```python
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "WhatsApp AI Agent"
    whats360_api_url: str = "https://api.whats360.com"
    whats360_token: str = ""
    openai_api_key: str = ""
    
    # Existing settings (keep or remove if unused)
    active_llm_provider: str = "openai"

def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 2: Create .env.example**
Create a template for environment variables.

```text
WHATS360_API_URL=https://api.whats360.com
WHATS360_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key_here
```

- [ ] **Step 3: Commit**
```bash
git add src/config/settings.py
git commit -m "config: add Whats360 and OpenAI settings"
```

---

### Task 2: Outbound API Service

**Files:**
- Modify: `src/api/outbound.py`

- [ ] **Step 1: Implement send_whats360_message**
Replace existing Meta-specific logic with Whats360 POST request.

```python
import requests
from src.config.settings import get_settings
from loguru import logger

def send_whats360_message(to_number: str, message_text: str):
    settings = get_settings()
    url = f"{settings.whats360_api_url}/messages/send"
    headers = {
        "Authorization": f"Bearer {settings.whats360_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": to_number,
        "text": message_text
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"Message sent to {to_number}: {message_text}")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send message to {to_number}: {e}")
        return {"success": False, "error": str(e)}
```

- [ ] **Step 2: Commit**
```bash
git add src/api/outbound.py
git commit -m "feat: implement Whats360 outbound service"
```

---

### Task 3: Agent Tools

**Files:**
- Modify: `src/agent/tools.py`

- [ ] **Step 1: Create WhatsApp Sender Tool**
Wrap the outbound function into a LangChain `@tool`.

```python
from langchain.tools import tool
from src.api.outbound import send_whats360_message

@tool
def whatsapp_sender(to_number: str, text: str) -> str:
    """
    Use this tool to send a WhatsApp message to a user.
    'to_number' should be the recipient's phone number in international format.
    'text' is the message body.
    """
    result = send_whats360_message(to_number, text)
    if result.get("success") or "id" in str(result):
        return "Message sent successfully."
    return f"Failed to send message: {result.get('error', 'Unknown error')}"
```

- [ ] **Step 2: Commit**
```bash
git add src/agent/tools.py
git commit -m "feat: add whatsapp_sender tool for agent"
```

---

### Task 4: LangChain Agent Service

**Files:**
- Create: `src/agent/service.py`

- [ ] **Step 1: Implement Agent Runner**
Create a function that initializes and runs the agent using `create_agent`.

```python
from langchain.agents import create_agent
from src.agent.tools import whatsapp_sender
from src.config.settings import get_settings
from loguru import logger
import os

def run_whatsapp_agent(sender_phone: str, user_message: str):
    settings = get_settings()
    
    # Ensure API key is in environment for create_agent/init_chat_model
    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key

    system_prompt = (
        f"You are a helpful WhatsApp assistant. The user's phone number is {sender_phone}. "
        "When you have a response, ALWAYS use the 'whatsapp_sender' tool to send it to the user. "
        "Do not just state the answer, use the tool."
    )

    try:
        # create_agent returns a LangGraph CompiledStateGraph
        agent = create_agent(
            model="gpt-4o",
            tools=[whatsapp_sender],
            system_prompt=system_prompt
        )
        
        # Invoke the agent with the user message
        agent.invoke({"messages": [("user", user_message)]})
        logger.info(f"Agent finished for {sender_phone}")
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
```

- [ ] **Step 2: Commit**
```bash
git add src/agent/service.py
git commit -m "feat: implement LangChain agent service"
```

---

### Task 5: Webhook Endpoint (FastAPI)

**Files:**
- Modify: `src/api/whatsapp.py`

- [ ] **Step 1: Implement Whats360 Webhook**
Replace Meta webhook with Whats360 structure and use `BackgroundTasks`.

```python
from fastapi import APIRouter, Request, BackgroundTasks
from src.agent.service import run_whatsapp_agent
from loguru import logger

router = APIRouter()

@router.post("/webhook/whats360")
async def handle_whats360_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
        logger.info(f"Received webhook: {data}")
        
        # Adjust extraction based on actual Whats360 payload
        # Standard assumption: {"phone": "...", "message": "..."}
        sender_phone = data.get("phone") or data.get("sender") or data.get("from")
        text_body = data.get("message") or data.get("text") or data.get("body")
        
        if sender_phone and text_body:
            background_tasks.add_task(run_whatsapp_agent, sender_phone, text_body)
            return {"status": "success", "message": "Agent triggered in background"}
        
        return {"status": "ignored", "reason": "Missing phone or message"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return {"status": "error", "message": str(e)}
```

- [ ] **Step 2: Commit**
```bash
git add src/api/whatsapp.py
git commit -m "feat: implement Whats360 webhook with BackgroundTasks"
```

---

### Task 6: Final Integration & Verification

**Files:**
- Modify: `src/main.py`

- [ ] **Step 1: Verify router inclusion**
Ensure the new webhook route is registered.

```python
from fastapi import FastAPI
from src.api.whatsapp import router as whatsapp_router

app = FastAPI(title="WhatsApp AI Agent")
app.include_router(whatsapp_router)
```

- [ ] **Step 2: Manual Verification Instructions**
1. Run server: `uvicorn src.main:app --reload`
2. Start ngrok: `ngrok http 8000`
3. Point Whats360 webhook to `https://<ngrok_url>/webhook/whats360`.

- [ ] **Step 3: Commit**
```bash
git add src/main.py
git commit -m "feat: final integration"
```
