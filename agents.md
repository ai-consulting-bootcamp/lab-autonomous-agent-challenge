# agents.md: Kleinanzeigen Lead Qualifier (staging app)

## Stack
Python 3.12 · Gradio 6 (theme and css in launch()) · LangChain (langchain-openai, langchain-pinecone) · OpenAI gpt-5.4-mini · text-embedding-3-small (512 dims) · Pinecone · Cohere Rerank · Airtable (pyairtable) · Render

## Run
- Install: `pip install -r requirements.txt`
- Local: `python app.py` → http://127.0.0.1:7860
- Render: start command `python app.py`; the app binds to 0.0.0.0 and $PORT

## Repo map
- `app.py`: Gradio UI (form tab, chat tab, about tab)
- `src/prompts.py`: system prompt, user template, output schema (same rules as the n8n workflow)
- `src/qualifier.py`: input guard → Pinecone search → Cohere rerank → LLM structured output → score check
- `src/airtable_store.py`: writes one record to the `Leads` table (20 fields)

## Conventions
- Beginner-friendly code, few lines, `#` comments
- Prompt rules change in `src/prompts.py` first, then are copied to the n8n Lead Qualifier Agent
- Airtable field names are fixed; they must match the n8n Create lead record node

## Definition of done (per card)
- Workbench notebook checks print PASS
- The four demo leads give the expected rating and sales team
- Existing behaviour unchanged (n8n workflow and Pinecone index untouched)

## Never do
- Commit `.env`, keys or tokens
- Write to the Pinecone index from the app (read only)
- Send emails or messages to leads
- Run git commands for Ayhan (he commits and pushes himself, on main)
