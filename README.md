# Kleinanzeigen Lead Qualifier (fictional demo)

Lead qualification agent for an Ironhack AI Consulting & Integration Bootcamp lab.
Concept demo with fictional data. Not affiliated with or endorsed by Kleinanzeigen.

**What it does:** a business describes itself in a form or chat. The agent searches a fictional 2026 offer knowledge base (Pinecone + Cohere reranker), scores the lead 0-100, rates it Hot / Warm / Cold / Needs review, picks the sales team, drafts a reply (a human sends it) and saves the record to Airtable.

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in the keys
3. `python app.py`

## Deploy to Render (staging)
1. New → Web Service → connect this repo
2. Build command: `pip install -r requirements.txt` · Start command: `python app.py`
3. Environment: add every variable from `.env.example`
4. Free plan: sleeps after 15 minutes idle and takes about a minute to wake

Related: n8n workflow `kleinanzeigen_lead_qualifier.json` (same prompt, index and table).
