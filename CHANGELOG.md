# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-04-26

### Added
- **Core Architecture:** Python/FastAPI backend with LangGraph orchestration.
- **Multi-Provider LLM:** Integrated LiteLLM for switching between OpenAI, Groq, OpenRouter, Gemini, and Replicate.
- **Data Retrieval:** SQLAlchemy models with `pgvector` for RAG and SQL lead retrieval.
- **WhatsApp Integration:** Direct Meta WhatsApp Business API integration (Webhooks + Outbound).
- **Brand Voice Guard:** `VoiceGuard` system to enforce "Expertise Amplification" tone and filter forbidden AI cliches.
- **Dynamic Config:** Support for `/set-model` command via WhatsApp to update agent behavior in real-time.
- **Testing:** Comprehensive test suite for config, LLM service, VoiceGuard, and Webhooks.
