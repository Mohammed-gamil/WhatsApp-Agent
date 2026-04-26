# Best Free Databases for your AI Agent

Your agent requires **PostgreSQL** with the **pgvector** extension for RAG capabilities. Here are the best free-tier providers:

## 1. Supabase (Recommended)
The easiest way to get started. 
- **Free Tier:** 500MB database, 5GB bandwidth.
- **pgvector:** Pre-installed and ready to use.
- **Best for:** Most projects. The unified SQL and Vector search is seamless.
- **Link:** [supabase.com](https://supabase.com)

## 2. Neon
A modern serverless PostgreSQL.
- **Free Tier:** 0.5 GiB storage, generous compute.
- **pgvector:** Supported.
- **Best for:** High performance and autoscaling.
- **Link:** [neon.tech](https://neon.tech)

## 3. Tembo
PostgreSQL managed service with specialized "Stacks."
- **Free Tier:** 1GB RAM, 10GB storage.
- **pgvector:** Fully supported via their "Vector Search" stack.
- **Best for:** If you want a more specialized vector experience.
- **Link:** [tembo.io](https://tembo.io)

## 4. Local Docker (Best for Dev)
If you aren't ready to deploy to the cloud yet, run it locally:
```bash
docker run --name agent-db -e POSTGRES_PASSWORD=pass -p 5432:5432 -d ankane/pgvector
```
- **Image:** `ankane/pgvector` comes with the extension pre-installed.

## How to enable pgvector on a new DB
Once connected to your new database, run this SQL command:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```
Your agent will then be able to create the `knowledge_documents` table correctly.
