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

Related: n8n workflow export at evidence/workflows/Kleinanzeigen Lead Qualifier.json (same prompt, index and table).

Render URL: I did not find the deployed URL in the repository files.

## Run the four demo leads

Start the app with `python app.py` to use the Gradio form and chat. To run all four labelled leads through the Python qualifier, open `workbench_finalize_docs.ipynb`, run the setup cell, then run the code cell whose first line says “Demo leads in app.py”. That cell reads `DEMO_LEADS` from `app.py`, calls `src.qualifier.qualify` for each lead, waits 7 seconds between leads and saves the results under `evidence/`. It does not save those four demo runs to Airtable.

Results: I measured 4/4 expected rating and team matches in the Python demo leads, an average qualification time of 2.475 seconds, a maximum of 3.9 seconds and an LLM cost of $0.001881 per lead. Airtable had no matching n8n demo records.
