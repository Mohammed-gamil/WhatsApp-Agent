# Task List

## Infrastructure
- [ ] Set up Production PostgreSQL with `pgvector` extension.
- [ ] Configure Environment Variables (`.env`) for all API Keys.
- [ ] Set up Dockerfile for containerized deployment.

## Agent Features
- [ ] Implement actual vector embedding logic in `src/agent/tools.py`.
- [ ] Add support for WhatsApp interactive buttons and templates.
- [ ] Implement Admin-only auth for `/set-model` commands.
- [ ] Add conversation history persistence to the database.

## Sales & Marketing
- [ ] Refine the RAG knowledge base with complete product documentation.
- [ ] Create and approve Meta WhatsApp Message Templates for initial outreach.
- [ ] Implement a lead-scoring system based on SQL data.

## Maintenance
- [ ] Add structured logging (e.g., Loguru or structlog).
- [ ] Set up CI/CD pipeline for automated testing.
