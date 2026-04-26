# WhatsApp AI Sales Agent

A sophisticated outbound sales agent that "Amplifies human expertise." Built with FastAPI, LangGraph, and LiteLLM to deliver a high-end, expertise-driven sales experience on WhatsApp.

## Features

- **Expertise Amplification:** Strictly avoids "AI-powered" cliches; focuses on human empowerment and tangible value.
- **Multi-Model Orchestration:** Use any provider (OpenRouter, Groq, OpenAI, Gemini) via a unified config.
- **Smart Tools:** Integrates RAG (Vector Search) and SQL (Lead Data) directly into the agent's decision loop.
- **Dynamic Configuration:** Adjust the agent's model or behavior directly through WhatsApp commands (e.g., `/set-model groq/llama3-70b`).
- **Direct Meta Integration:** Uses Meta's WhatsApp Business Cloud API for high-performance messaging.

## Project Structure

```text
├── src/
│   ├── api/          # FastAPI routes (WhatsApp Webhooks, Outbound)
│   ├── agent/        # Core AI logic (LangGraph, LiteLLM, Tools, VoiceGuard)
│   ├── config/       # Global settings and environment management
│   └── database/     # SQLAlchemy models and pgvector session
├── tests/            # Full test suite
├── requirements.txt  # Python dependencies
├── CHANGELOG.md      # Version history
└── TODO.md           # Roadmap and tasks
```

## Setup & Deployment Steps

### 1. Prerequisites
- **Python 3.11+**
- **PostgreSQL** with the `pgvector` extension installed.
- **Meta Developer Account** with a WhatsApp Business App set up.

### 2. Installation
```bash
# Clone the repository
# git clone <repo-url>
# cd Whatsapp-agent

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
# Meta WhatsApp API
META_VERIFY_TOKEN=your_custom_token
META_ACCESS_TOKEN=your_permanent_system_user_token

# LLM Providers (Set whichever you plan to use)
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-...

# Database
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/your_db
```

### 4. Running Locally
```bash
# Start the FastAPI server
# PYTHONPATH=. is required to resolve modules correctly
$env:PYTHONPATH="."; uvicorn src.main:app --reload
```

### 5. Exposing for Webhooks (Testing)
Meta requires an HTTPS endpoint for webhooks. Use `ngrok` to expose your local port:
```bash
ngrok http 8000
```
Copy the HTTPS URL from ngrok (e.g., `https://xyz.ngrok-free.app`) and set it in your **Meta Developer Portal**:
- **Callback URL:** `https://xyz.ngrok-free.app/webhook`
- **Verify Token:** The value of `META_VERIFY_TOKEN` from your `.env`.

### 6. Verification
Run the test suite to ensure everything is configured correctly:
```bash
$env:PYTHONPATH="."; pytest tests -v
```

## Deployment Best Practices
- **Database:** Use a managed service like Supabase or AWS RDS that supports `pgvector`.
- **Hosting:** Deploy via Docker or to platforms like Railway, Render, or Google Cloud Run.
- **Security:** Ensure `/set-model` commands are guarded by phone number white-lists in `src/agent/graph.py`.
