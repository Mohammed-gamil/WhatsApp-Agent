# Design Document: WhatsApp AI Agent (Whats360)

## Overview
A microservice built with FastAPI and LangChain to handle WhatsApp conversations via the Whats360 gateway. The system receives webhooks, processes messages in the background using an AI agent, and replies autonomously via a LangChain tool.

## Tech Stack
- **Framework**: FastAPI (Async API)
- **Agent Framework**: LangChain (ReAct Agent)
- **LLM**: OpenAI (GPT-4o or gpt-3.5-turbo)
- **HTTP Client**: Requests (for outbound)
- **Environment**: python-dotenv

## Architecture
1. **Inbound**: `POST /webhook/whats360`
   - Receives JSON payload from Whats360.
   - Extracts `sender` (phone number) and `message` (text).
   - Returns `200 OK` immediately.
   - Dispatches `BackgroundTasks` to run the agent.
2. **Agent Logic**:
   - Initializes a LangChain ReAct agent.
   - Injects the `sender` phone number into the `whats360_sender` tool's context.
   - Uses a system prompt to guide the agent to reply via the tool.
3. **Outbound**: `whats360_sender` Tool
   - Makes a POST request to `WHATS360_API_URL/messages/send`.
   - Headers: `Authorization: Bearer WHATS360_TOKEN`.
   - Payload: `{"to": "<phone>", "text": "<message>"}`.

## Project Structure (Revised)
```
src/
├── main.py              # FastAPI app entry point
├── config/
│   └── settings.py      # Env var management
├── api/
│   ├── outbound.py      # Whats360 API service
│   └── whatsapp.py      # Webhook route
└── agent/
    ├── service.py       # LangChain Agent setup
    └── tools.py         # Agent tools (whatsapp_tool)
```

## Environment Variables
- `WHATS360_API_URL`: Base URL for Whats360 (e.g., https://api.whats360.com)
- `WHATS360_TOKEN`: API Token
- `OPENAI_API_KEY`: OpenAI Key

## Error Handling
- Webhook catches parsing errors and logs them but still returns 200 to prevent loops.
- Outbound service uses try/except and logs failure details.
- Agent is wrapped in a try/except to ensure background task completion.

## Testing Strategy
- Use `ngrok` to expose localhost:8000.
- Configure Whats360 dashboard with the ngrok URL: `https://<id>.ngrok.io/webhook/whats360`.
- Unit tests for `outbound.py` and `agent/service.py` logic.
