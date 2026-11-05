# Autonomous Agent Project Plan: Unioptt Catalogue Verification Agent

**Product:** Unioptt, a university matching platform for Turkish students who want to study in Europe (live: unioptt.netlify.app)
**This plan:** the agent extension I will build as my bootcamp project (solo, 2 weeks)

---

## 1. Use Case

### Problem
In Türkiye, university entry depends on one central exam (YKS). Good public universities need very high scores, and good private universities are too expensive for most families. That is why many students look abroad.

Abroad, they meet a second problem: most consultancies and agencies are **paid by foreign institutions** and work under commission pressure. They steer students toward the institutions that pay them. Students and families rarely get an **objective** selection process.

Unioptt was designed to fix this: it shows students many different options, ranked by how well each programme fits **them** (interests, personality, academic profile, budget, lifestyle), not by who pays a commission.

**The problem this agent solves:** Unioptt's matching engine is only as trustworthy as its programme catalogue. Today all 94 programmes are hand-entered in one static JSON file with **no provenance**: no source URL, no verification date, no record of who entered a value. Tuition, deadlines and language requirements change every year, and nobody can say where a number came from or when it was true.

> The numbers that drive the ranking are the least-sourced numbers in the system.

For a product whose promise is *objectivity*, this is the weakest point.

### Target users
- **Primary:** Turkish high school students and graduates who want to study in Europe, and their **families**
- **Secondary:** teachers and school counsellors who advise them
- **Later:** high schools as institutional users
- **Users of the agent itself:** the Unioptt team (me), who approve verified data before it reaches students

### Current process
**How students choose today (without Unioptt):**
1. Take the YKS exam and get a score.
2. Compare limited domestic options: high-scoring public universities or expensive private ones.
3. Look abroad: search university websites, rankings, social media groups, and visit agencies.
4. The agency recommends programmes, often those of partner institutions that pay commission.
5. The family decides with incomplete, possibly biased information.

**How the Unioptt catalogue is maintained today:**
1. Programme data is researched by hand and typed into `programs.json`.
2. The file is read on every matching run.
3. There is no update cycle, no source tracking and no check whether a value is still correct.

**With the agent:**
1. Every week, the agent picks programmes whose facts are Unknown, Inferred or older than 90 days.
2. It searches the official source (university page, national portal), extracts the facts and the source URL.
3. It compares them with the catalogue and flags differences.
4. A human approves or rejects each proposed change.
5. Approved records are marked **Verified** with source, date and approver.

### Unioptt user journey (context)
1. Register (birth year decides the next step)
2. Parental consent for under-18s (KVKK): a code is emailed to a parent
3. Profile in five steps: academics, grades, motivation, lifestyle, constraints
4. Assessment: RIASEC, OFFPP and MPQ-40 (116 items), scored 0–100
5. Matching: 94 programmes scored in five stages (career, curriculum, university, city, country) with hard gates
6. Explore results: Best Fit, Dream, Safe, Hidden Gems, each with score, confidence, cost and reasons
7. Shortlist (up to 5) and compare
8. Prepare: readiness score, task list, timeline, scholarships, requirements marked Verified / Inferred / Unknown
9. Reports for the student and a separate parent report (raw psychometric scores withheld)

The agent improves steps 5–8 by making the data underneath them traceable.

### Why it works (validation so far)
- The idea was valued by a small sample group of target users [n = __ , to fill].
- The product was tested in a basic form; the core journey works end to end and is live.

### How we know the agent is working
- Every verified record has a `source_url`, `last_verified` and `verified_by`
- In a test set, the extracted facts match the official source when checked by hand
- The agent never changes a record without human approval
- The agent reports "not found" instead of guessing when the source does not contain a fact

---

## 2. Technology Stack

### Framework answers
| Question | Answer | Consequence |
|---|---|---|
| External knowledge? | **Yes**: official university pages and portals | RAG over fetched pages |
| External systems? | **Yes**: web sources, Supabase, Telegram | Tools + integrations |
| Multi-step reasoning? | **Yes**: select → fetch → extract → compare → approve → write | LangGraph state machine |
| Business system integration? | **Yes**: scheduling, notifications | n8n |
| Autonomous? | **Yes**: weekly runs without input, human only approves | Scheduling, error handling, monitoring |

### Stack
| Layer | Choice |
|---|---|
| Existing product | FastAPI, SQLAlchemy 2.0 async, Pydantic v2 (backend) · Next.js 14 (frontend) · Render (API) · Netlify (frontend) · Supabase Postgres |
| Core LLM | OpenAI `gpt-4o-mini` for extraction (cheap, enough for structured extraction) |
| RAG | Fetch official page → chunk → embed (`text-embedding-3-small`) → retrieve + rerank (Cohere) → extract with source quote |
| Agent framework | **LangGraph**: fixed path with one human-approval step |
| Orchestration | **n8n**: weekly schedule, calls a FastAPI endpoint, sends a Telegram summary ("3 changes waiting for approval") |
| Storage | Programme catalogue moves from `programs.json` to a **Supabase table** with provenance fields |

### Justification
- **Matching stays deterministic.** No ML or LLM in the ranking. With minors as users, explainability matters more than flexibility: the same input always gives the same ranking, and every run is logged with inputs, scores and engine version.
- **The agent sits beside the engine, not inside it.** The LLM only verifies **facts**. It never creates or changes **judgement scores** (`quality_score`, `industry_demand_score`, `city_safety_score`, `primary_riasec`); these need a documented human rubric.
- **LangGraph over a free agent:** the path is known in advance and must be auditable (lesson from the LangGraph vs. agent labs).
- **n8n for the "doing":** schedule, notification and error alerts without building them in code.
- **Python only:** the backend is already Python, so the agent reuses Pydantic models and the database layer.

### Alternatives considered
| Alternative | Why not (for now) |
|---|---|
| Free LangChain agent with web search | Less predictable path, harder to audit |
| Scraping all of Europe + UK | Too big for 2 weeks; terms-of-use and maintenance risk |
| LLM-based ranking | Loses explainability; risky with minors |
| Keep JSON file, add fields | No safe concurrent writes, no migrations, no audit history |

### Trade-offs
- Human approval slows updates, but prevents wrong data reaching students.
- One country first means limited coverage at launch.
- LLM extraction costs money per page and can misread pages; every value is stored with its source quote so it can be checked.

---

## 3. MVP Scope

### All possible features (brainstorm)
Provenance fields · catalogue in database · fact verification agent · human approval · weekly schedule · Telegram notifications · discrepancy report · scholarship verification · deadline alerts for students · coverage for all EU countries + UK · judgement-score rubric · automatic re-matching after data changes · admin dashboard · source change detection · multilingual sources (DE, NL, FR…)

### Must-have (MVP, bootcamp)
- Programme catalogue in Supabase with `source_url`, `last_verified`, `verified_by`, `status` (Verified / Inferred / Needs Review / Unknown)
- Verification agent for **one country** and **three facts**: tuition, application deadline, language requirement
- Human approval before any record changes
- n8n weekly schedule + Telegram summary
- Discrepancy log (old value, new value, source, date)

### Should-have (v2)
- More countries
- Scholarship data verification
- Admin view for approvals (instead of Telegram)
- Rubric documents for judgement scores

### Nice-to-have (v3+)
- All of Europe + UK via national portals
- Deadline reminders to students
- Automatic re-matching when data changes
- Change detection on source pages

### Out of scope (MVP)
- Changing the matching engine or its scores
- Any automated creation of judgement scores
- Student-facing changes beyond showing source and "last verified"
- Processing student personal data in the agent

### Success metrics
| Metric | Today | MVP target |
|---|---|---|
| Programmes (in scope) with `source_url` | 0% | 100% |
| Verified in last 90 days | 0% | ≥ 80% |
| Extraction accuracy (manual spot check) | – | ≥ 90% |
| Changes written without approval | – | 0 |
| Discrepancies found between catalogue and source | unknown | reported (any number is a finding) |
| Cost per verification run | – | measured, target < $1 |

---

## 4. Risk Assessment

| Risk | Category | P | I | Mitigation |
|---|---|---|---|---|
| Agent extracts a wrong value (hallucination, misread page) | Technical | M | H | Store the source quote with each value; human approval; "not found" allowed |
| Agent "fills in" judgement scores | Technical / Data | M | H | Explicit rule: facts only; schema prevents agent writes to judgement fields |
| Official pages change layout, block bots or are missing | Technical | H | M | Retry + "Needs Review" status; respect robots.txt and terms; manual fallback |
| Wrong deadline or tuition reaches a student | Data / Business | M | H | Only Verified data shown as fact; others labelled Inferred / Unknown |
| Codebase untouched for ~2.5 months | Technical | M | M | Phase 0: run locally, check dependencies and deploys first |
| Schema change without migrations (Alembic unused, tables via `create_all`) | Technical | M | M | Start using Alembic with this change |
| API costs grow with pages | Business | L | M | Limit to one country, cache pages, cheap model, cost per run logged |
| Scope creep (all of Europe) | Business | H | H | Hard limit: 1 country, 3 facts in MVP |
| Personal data of minors (platform-wide, GDPR + KVKK) | Data | M | H | Agent does not touch student data; check Supabase/Render region (EU); parental consent flow exists |
| Self-declared birth year / parent email can be bypassed | Data | M | M | Name as residual risk; review stronger verification in v2 |
| Assessment instrument licences (OFFPP, MPQ-40) | Business | M | M | Check licence and validation status before commercial use; RIASEC (O*NET) is public domain |
| Long onboarding (116 items + 5 steps) causes drop-off | Business | H | M | Measure completion rate; add save & resume |

---

## 5. Implementation Plan (solo, 2 weeks)

| Phase | Days | Work | Milestone |
|---|---|---|---|
| 0 · Setup | 1 | Run backend + frontend locally, check Render / Supabase / Netlify, update dependencies | Product runs locally |
| 1 · Data preparation | 2–3 | Alembic migration: `programs` table with provenance fields; import `programs.json`; all statuses start as Unknown / Inferred | Catalogue in database |
| 2 · Core agent | 4–5 | LangGraph: select → fetch → chunk/embed → retrieve/rerank → extract (with quote) → compare → approval → write; one country, 3 facts | One programme verified end to end |
| 3 · Integration & testing | 2 | FastAPI endpoint; n8n schedule + Telegram summary + error workflow; manual accuracy check on a test set | Weekly run works without me starting it |
| 4 · Deployment & monitoring | 2 | Deploy, metrics, demo, documentation | Demo + metrics |

**Dependencies:** Phase 2 needs the database table (Phase 1). Phase 3 needs a working agent endpoint (Phase 2).

### Resources
- **Team:** solo (product, engineering, data, approval)
- **Tools:** VS Code, Python, LangGraph, n8n, Supabase, Render, Netlify, Telegram bot
- **Budget:** existing hosting plans; OpenAI and Cohere usage for one country (expected a few dollars in the MVP, measured per run)

---

## 6. Success Metrics
See the table in section 3. In short, the MVP succeeds when:
1. Every programme in scope has a source and a verification date
2. Spot-checked values match the official source in at least 9 of 10 cases
3. No record changes without my approval
4. The weekly run happens without me starting it, and failures alert me

---

## Prototype and verification evidence
*(Optional prototype, Step 6)*

As a first building block I built the **intake workflow** in n8n: Telegram Trigger → Edit Fields → Airtable (W5D2 lab).
- Input: a Telegram message, e.g. "I want to study psychology in Germany. What are my options?"
- Output: one structured record (Name, Message, Chat ID, Timestamp) in Airtable
- Execution trace: 3 nodes, success in 726 ms
- Details: see `lab_proof.md` of the Telegram → Airtable lab

**Learned:** the source payload is not always complete (no `username`), dates need conversion (Unix → ISO → UTC), and field names must match the destination exactly. All three will apply to the verification agent: official pages will be incomplete, dates come in many formats, and the catalogue schema must be strict.

---

## Explain: first failure mode to monitor if this ran daily
**A wrong value that looks correct.** The run reports "success", but the agent extracted the wrong tuition or deadline (e.g. from last year's page, or EU vs. non-EU fees). It would not crash; it would quietly mislead.

**Monitoring:**
- every value stored with its source quote, so the approver can check it in seconds
- alert when a value changes by more than a threshold (e.g. tuition ±30%)
- weekly count of "Needs Review" and "not found" results; a sudden jump means a source changed
- n8n Error Workflow for runs that fail completely
