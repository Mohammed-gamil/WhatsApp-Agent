# WhatsApp AI Agent (Whats360) Setup Guide

This project is a modular, asynchronous WhatsApp AI Agent built with FastAPI and LangGraph, specifically tailored for the Whats360 API.

## 🚀 How to Run Locally

### 1. Install Dependencies
Ensure you have Python 3.10+ installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Edit the `.env` file in the root directory:
- `WHATS360_TOKEN`: Your API token.
- `WHATS360_INSTANCE_ID`: Your instance ID (e.g., `agent`).
- `OPENAI_API_KEY`: Your OpenAI API key for the agent logic.

### 3. Start the Server
Run the application using Uvicorn:
```bash
python -m app.main
```
The server will start at `http://localhost:8000`.

## 🌐 Exposing to the Internet (Ngrok)

Whats360 needs a public URL to send webhooks to. Use Ngrok to expose your local server:

1.  **Start Ngrok**:
    ```bash
    ngrok http 8000
    ```
2.  **Copy the Forwarding URL**: It will look like `https://a1b2-c3d4.ngrok-free.app`.
3.  **Set the Webhook in Whats360 Dashboard**:
    - Go to your Whats360 instance settings.
    - Set the Webhook URL to: `https://your-ngrok-url.app/api/v1/webhook/whats360`.

## 🤖 Features
- **Auto-formatting**: Automatically converts phone numbers to `@s.whatsapp.net` JIDs.
- **Background Processing**: Webhooks return 200 OK immediately; the AI reasons and replies in the background.
- **Multimodal Tools**: The agent can send text, images, and documents.
- **Campaign Management**: The agent can autonomously create and launch marketing campaigns.
- **Stateful Memory**: Built with LangGraph for complex, multi-turn conversations.

## 🛠 Project Structure
- `app/services/whats360.py`: The core API client handling GET/POST requests and URL encoding.
- `app/agent/tools.py`: LangChain tools that the agent uses to interact with WhatsApp.
- `app/agent/graph.py`: The LangGraph definition of the AI's "brain".
- `app/api/webhook.py`: The FastAPI route that receives incoming WhatsApp messages.
