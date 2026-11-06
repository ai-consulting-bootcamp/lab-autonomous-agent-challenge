# Autonomous Agent Challenge — Lab Proof & Project Plan

**Project:** AI Food Concierge  
**Lab:** Autonomous AI Systems — Scoping & Project Planning  
**Status:** Planning completed; local deterministic proof and optional n8n agent tests performed  
**Last updated:** 6 November 2026

> **Submission transparency:** Steps 1–5 are documented below. Optional Step 6 has now been tested in two distinct forms: (1) a local deterministic Python fallback with saved input/output/trace fixtures, and (2) an n8n AI Agent using a fictional restaurant-search Code Tool, tested interactively on 6 November 2026. A sanitized workflow export is included at `workflows/ai_food_concierge_workflow.json`. The n8n chat replies and one actual tool result were observed during testing, but a downloadable n8n execution trace / execution ID has **not** been provided; the local Python trace is **not** an n8n trace.

---

## 1. Use Case and Business Context (Step 1)

### 1.1 Project overview

**AI Food Concierge** is a conversational restaurant-discovery service. Users can describe vague or specific dining preferences in natural language, and an autonomous AI agent searches restaurant information, compares options, follows up on missing details, and suggests relevant alternatives.

The **long-term vision** is a central food-service platform combining restaurant discovery, table reservations, restaurant services, and eventually food delivery. The **first MVP** is deliberately narrower: **autonomous restaurant exploration and personalized recommendations** in one pilot city.

### 1.2 Problem statement

Visitors and residents often struggle to discover restaurants that fit their preferences. Restaurant details, menus, booking methods, and availability are fragmented across maps, search engines, restaurant websites, and reservation services. Users must repeatedly search, compare options, and sometimes telephone restaurants just to learn whether a visit is possible.

### 1.3 Target users and stakeholders

- **Primary users:** Local residents, students and other digitally confident users, and visitors unfamiliar with a city's restaurants.
- **Secondary stakeholders:** Restaurant owners and operators who want visibility, customer acquisition, and—later—simpler digital reservation-management options.
- **Pilot positioning:** Start with a digitally engaged local audience; tourism is a benefit, not the initial positioning or primary city-selection criterion.

### 1.4 Current manual process

1. Search via Google, maps, recommendations, or individual websites.
2. Compare restaurants by location, cuisine, menu, price, and atmosphere.
3. Find a reservation channel and check availability, often by opening another platform or calling.
4. Restart the search when a restaurant is unsuitable, unreachable, or fully booked.

### 1.5 Primary value proposition

**Autonomous Exploration & Recommendations:** The concierge can understand open-ended dining wishes, explore several database-backed options, evaluate their fit, and suggest alternatives—rather than forcing the user to know exactly what they want and repeatedly apply static filters.

Supporting value propositions:

- **Conversational discovery:** Natural-language interaction, contextual follow-up questions, and clarification of vague preferences.
- **Exploratory discovery:** Users may encounter suitable restaurants they did not previously know.
- **Contextual answers:** Explain recommendations and answer questions using available restaurant records.
- **Integrated service vision:** Eventually connect discovery with reservations, menus, and food orders.

**Competitive caveat:** These benefits are product hypotheses, not yet proven competitive advantages. They must be tested against the user experience of existing restaurant platforms.

### 1.6 Verification criteria for the use case

The system should demonstrate that it can:

1. Extract and retain relevant preferences (e.g., city, cuisine, budget, date, time, party size) from multiple chat turns.
2. Retrieve restaurants matching the known preferences.
3. Perform bounded alternative searches when initial results are unsuitable.
4. Explain the recommendations using factual database information and explicitly acknowledge unknown data.
5. Identify whether an online booking channel is documented (`yes`, `no`, or `unknown`) without implying live table availability.
6. Handle incomplete requests and empty search results appropriately.

A successful database write alone is **not** sufficient evidence of recommendation quality.

### 1.7 Pilot city strategy

**Provisional first choice:** Heidelberg. **Alternative:** Aachen. These choices are planning hypotheses from an initial comparison; they are **not** a completed market or restaurant-partner feasibility assessment.

Agreed weighting for city selection:

| City selection criterion | Weight |
|---|---:|
| Restaurant density and diversity | 25% |
| Digital readiness of restaurants | 25% |
| Student and digital-native population | 20% |
| Partner acquisition feasibility | 20% |
| Dynamic restaurant market | 5% |
| Tourism potential | 5% |
| **Total** | **100%** |

The final city will be chosen only after checking local restaurant-data availability, actual partner interest, and integration feasibility. Geographic concentration is preferred over launching with thin coverage in many cities.

---

## 2. Technology Selection (Step 2)

### 2.1 Scoping questions

| Question | Decision | Reasoning |
|---|---|---|
| External knowledge required? | **Yes** | Restaurant facts must come from a maintained source, not solely the LLM's general knowledge. |
| RAG required? | **No, not for the MVP** | Core data is structured and can be filtered directly. RAG may help later with large or unstructured menus and documents. |
| Interactions with external systems? | **Eventually yes** | Reservation providers and restaurant-managed information can supply additional data, subject to authorized access. |
| Multi-step reasoning? | **Yes, bounded** | The agent should select tools, evaluate results, and explore reasonable alternatives. |
| Business-system orchestration? | **Yes** | n8n fits tool and data orchestration and the team's existing experience. |
| Autonomous operation without a person at every step? | **Limited** | Search and recommendation can be autonomous; booking and other consequential transactions require later controls. |

### 2.2 Proposed stack

| Layer | Proposed approach | Purpose |
|---|---|---|
| Conversational interface | Simple chat UI | Natural-language requests and follow-ups |
| Core model | LLM through a configurable provider (specific model TBD) | Understand intent, extract preferences, explain results |
| Agent/orchestration | **n8n AI Agent** and workflow nodes | Select tools, route actions, coordinate steps and errors |
| Framework | LangChain components available through n8n | Tool-enabled AI interactions without unnecessary separate implementation |
| Database | **PostgreSQL** (proposal; SQLite possible for a small PoC) | Structured restaurant records and relevant state |
| Memory/state | Conversation memory plus structured request state | Preserve details across messages; validate required fields per action |
| Tool access | Narrow, validated database/API tools | Search restaurants; fetch restaurant details; conditionally query availability |
| Optional future retrieval | RAG / vector search | Unstructured menus, policies, or long-form content, if required |
| Optional future agent framework | LangGraph | More complex durable, stateful workflows, if n8n is insufficient |

### 2.3 Proposed workflow — conceptual, not executed

```text
User chat message
    -> n8n chat trigger
    -> LLM intent detection + preference extraction
    -> merge with structured conversation state
    -> route by intent
         |-- Discovery: search restaurants -> evaluate -> optional alternative search
         |-- Restaurant questions: retrieve known details -> grounded answer
         |-- Availability: validate date/time/party size -> authorized source, if enabled
         `-- Reservation request: explain booking options; no booking action in MVP
    -> validate and qualify factual statements
    -> conversational reply + limited operational logging
```

**Progressive slot filling:** The chat must accept incomplete requests (e.g., “I feel like Greek food”). Date, time, and party size become required only for an actual availability check; additional details and explicit consent would be required for a future binding reservation. Deterministic validation should guard critical tool calls rather than leaving all validation to the LLM.

**Bounded autonomy:** The agent may search iteratively, but only with approved read tools, limits on tool calls, clear fallback behavior, and transparency about alternatives. It may not fabricate restaurant facts, reservations, or live availability.

### 2.4 Integration strategy and trade-offs

**Long-term approach: hybrid.** Prefer authorized third-party reservation APIs where available; for restaurants without accessible systems, consider a minimal restaurant-managed availability interface. A normalized internal integration interface could hide provider-specific formats.

Advantages include reduced need to replace restaurant software, wider potential coverage, and lower dependence on one provider. Trade-offs include third-party access restrictions and the new operational burden of keeping manually entered data current.

**Important distinction:** Building our own adapter does not grant access to a third party's restricted data. Developing a full table/booking management system is a separate, larger product, not part of the first MVP.

---

## 3. MVP Scope (Step 3)

### 3.1 Must-have (initial MVP)

- Conversational chat for both vague and specific food requests.
- Intent and preference extraction from natural language.
- Memory and structured state across chat turns.
- Curated restaurant records for **one** pilot city.
- Database-backed filtering and restaurant-detail lookup.
- **Bounded autonomous exploration:** compare options and perform an additional relevant search when useful.
- Grounded, understandable recommendations and explanation of fit.
- Booking-channel information when known (`online available`, `not listed`, or `unknown`); never equate this with free tables.
- Clear handling of missing, outdated, or unverified information.
- Basic validation, access limits, error handling, and logging.

### 3.2 Conditional MVP feature

**Live availability checking** is included only if Phase 1 establishes reliable, authorized, and reasonably affordable access to reservation data for a useful pilot subset. Without such access, the MVP still launches as autonomous discovery, with links or instructions for existing booking channels where those are verified.

Simulated availability may demonstrate tool behavior during technical testing, but must be identified as simulated and never presented to users as confirmed availability.

### 3.3 Should-have (v2)

- Direct reservation creation, confirmation, modification, and cancellation.
- Extended menu and restaurant Q&A.
- Restaurant self-service portal for managing information.
- Automated review reminders and confirmations of stored restaurant data.
- Additional authorized booking-system integrations.

### 3.4 Nice-to-have (v3+)

- Food ordering and delivery-service integration.
- Interactive seating plans and preferred-table selection.
- Long-term preference personalization.
- Broader multi-city rollout and advanced restaurant analytics.

### 3.5 Explicitly excluded from initial MVP

Binding table reservations, payment processing, food ordering, delivery operations, a complete restaurant reservation management suite, full seating plans, unrestricted web search, and a complex multi-agent platform.

### 3.6 Scope-control rule

A feature enters the MVP only if it materially supports the central value proposition—**autonomous restaurant exploration and recommendations**—and its data, operational costs, and risks are realistic for a one-city pilot. Additional requests are recorded for later versions rather than silently added to MVP delivery.

---

## 4. Risk Assessment (Step 4)

**Method:** Probability and impact are preliminary **Low / Medium / High** judgments, to be revisited during feasibility checks and testing.

| Type | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| Business | Established restaurant-discovery competitors | High | High | Focus on conversational autonomous exploration; validate differentiated value through user tests. |
| Business | Chicken-and-egg adoption problem (users vs. restaurants) | High | High | Concentrate on one city, curate initial coverage, and validate demand before expansion. |
| Business | Low digital maturity or partner interest | Medium | High | Low-friction onboarding, initial use of permissible existing data, and early outreach. |
| Business | Low user adoption despite functional product | Medium | High | Compare with current search habits, collect feedback, and refine core user journeys. |
| Business | Unclear monetization or conflicts with recommendation neutrality | Medium | Medium | Test business-model assumptions separately; distinguish sponsored placement from organic relevance. |
| Data | Outdated restaurant menus, hours, or facilities | High | High | Track sources, `last_updated` and `last_verified`; enable corrections and scheduled reviews. |
| Data | Lack of reliable booking/API information | High | High | Treat availability as conditional; never claim a table is free without verified data. |
| Technical | Hallucinated restaurant attributes or amenities | Medium | High | Ground claims in structured tool results; represent unknowns explicitly; test missing-data cases. |
| Technical | Incorrect understanding of user preferences | Medium | High | Structured extraction, carry-over state, clarification questions, and checks on critical needs. |
| Technical | Provider/API outage, changed terms, or rate limits | Medium | High | Validate access early, limit retries, monitor errors, and degrade gracefully to discovery-only. |
| Legal / Data | Privacy and security issues involving chat or partner data | Medium | High | Data minimization, access restrictions, retention rules and legal review before public use. |
| Operational | Uncontrolled LLM/tool-call costs | Medium | Medium | Tool-call caps, usage alerts, model choice, and cost monitoring. |

### 4.1 Hybrid data freshness approach

- The platform tracks each restaurant fact's source and verification status.
- Restaurants may later receive a compact periodic summary and confirm or correct it.
- Where lawful and accessible, authorized updates can also be automated.
- No restaurant response must **not** be misrepresented as confirmation.
- Restaurants with overdue verification can remain discoverable with a neutral **information freshness notice**, allowing users to validate details directly.
- Higher-risk data requires stricter treatment: no unverified live availability or unsupported allergy-safety claims.

Automated restaurant reminders and a full self-service portal are **future-phase features**; basic metadata, manual correction procedures, and transparent uncertainty are appropriate for the MVP.

### 4.2 Operational boundaries

The agent should never silently convert an alternative (different cuisine, time, or location) into an exact match. It must label the trade-off and ask for confirmation before any future consequential action. Outputs should distinguish **known**, **not available**, and **unknown** information where applicable.

---

## 5. Implementation Plan (Step 5)

The plan assumes a small team, a limited restaurant dataset, and no major legal or API-access blockers. Durations are estimates, **not commitments**. Some tasks may overlap.

| Phase | Activities | Estimated duration | Milestone / deliverable |
|---|---|---:|---|
| **1. Market & Technical Feasibility** | Confirm pilot city, data sources, possible API permissions, and restaurant-partner assumptions; determine conditional availability decision. | 1–2 weeks | Pilot city and data/integration go/no-go |
| **2. Setup & Data Preparation** | Define schema and metadata, collect permitted restaurant data, set up database and n8n environment. | 1–2 weeks | Curated data source available to tools |
| **3. Core Agent Development** | Implement chat, extraction, state, read tools, dynamic alternatives, bounded autonomy and responses. | 2–3 weeks | Functional discovery prototype |
| **4. Integration & Testing** | Test varied requests, missing fields, factual grounding, tool failures, limits and conditional availability if approved. | 1–2 weeks | Acceptance tests passed or documented gaps |
| **5. Pilot Deployment & Monitoring** | Controlled pilot, user feedback, monitoring of errors, recommendation quality and costs. | 1–2 weeks | Pilot evaluation and next-phase decision |

**Estimated total: roughly 6–11 weeks**, before any adjustment for staffing, procurement, partner approvals, or integration delays.

### 5.1 Key dependencies / decision gates

1. **Feasibility gate:** Can we source sufficient accurate restaurant data for a meaningful pilot?
2. **Availability gate:** Is there an authorized and reliable external data path? If not, ship discovery without availability claims.
3. **Quality gate:** Do evaluation results support exposing recommendations to pilot users?
4. **Deployment gate:** Are privacy, access controls, operating costs, ownership, and incident handling adequately addressed?

### 5.2 Resources and responsibilities

| Role | Responsibility |
|---|---|
| AI Consultant / Product Lead | Business alignment, use-case scope, requirements, success measures, risk review |
| Automation / AI Developer | n8n orchestration, LLM integration, tool design, state management |
| Data / Integration Support | Restaurant schema, data sourcing, API feasibility, data-quality procedures |
| QA / Pilot Coordinator | Scenario tests, feedback collection, pilot operations and stakeholder coordination |

Some roles may be combined in a small team, but responsibilities should remain clear.

**Proposed services:** n8n, a hosted or local PostgreSQL database, LLM API, simple chat interface, basic logging/monitoring, and approved restaurant data sources.

### 5.3 Budget approach

A firm monetary budget cannot be justified yet. The first budget estimate should separate:

- One-time scoping, data preparation, development, QA and integration effort.
- Recurring LLM usage, hosting, monitoring and support.
- Conditional third-party API, partner, and legal/compliance costs.
- Contingency for data cleaning, provider restrictions, and unexpected evaluation work.

A usage model and cost ceiling should be set before the pilot is made publicly available.

---

## 6. Success Metrics and Acceptance Criteria

These are **proposed targets for planning**, not observed results. Testing needs a representative labeled scenario set and agreed evaluation rubric before percentages can be interpreted.

| Metric | Proposed target | Verification |
|---|---|---|
| Intent / preference extraction | ≥90% correct on defined cases | Compare extracted fields with human-labeled requests |
| Recommendation relevance | ≥85% of evaluated cases yield at least one suitable suggestion | Human-rated match against documented preferences and available records |
| Missing-information behavior | ≥95% of relevant cases handled appropriately | Test unclear, incomplete and conflicting requests |
| Factual grounding | No unsupported *critical* claims in the agreed acceptance set | Cross-check generated claims with retrieved data and verification status |
| Alternative-search behavior | ≥90% success on applicable test scenarios | Evaluate cases where initial results are empty or unsuitable |
| User value vs. current workflow | Observable improvement in task completion or user satisfaction | Controlled user trial / comparative tasks; threshold determined during pilot design |

**Acceptance conditions:** Users can start with vague requests, refine preferences conversationally, receive database-supported recommendations, and get relevant alternative suggestions within limits. The system communicates unknown or outdated facts and degrades safely during failed lookups. A confirmed booking is **not** an MVP acceptance requirement. Conditional live availability becomes a required acceptance criterion only if that feature passes its feasibility gate.

### Continuous improvement

Review unsuccessful searches, recurring clarification problems, user feedback, tool errors, outdated records and API spend. Improve structured prompts, search strategy, curated data, and validation rules as needed. Automatic model retraining is not part of this initial plan.

---

## 7. Lab Proof of Learning — Evidence Status

The lab describes a narrow **trigger → transform → action** path and asks for evidence that data moves from input to output. A deterministic local Python fallback was executed and saved, and a separate, optional n8n AI Agent was subsequently assembled and tested interactively. These are **different implementations** with different levels of evidence.

| Requested evidence | Status | Notes |
|---|---|---|
| Use case, technology design, MVP scope, risks | **Documented** | Sections 1–4 |
| Project phases, resources, timeline, success metrics | **Documented** | Sections 5–6 |
| Workflow export/configuration | **Available** | Sanitized n8n export: `workflows/ai_food_concierge_workflow.json`; local assembly notes: `workflows/README.md` |
| Example input payload | **Available** | Local file `fixtures/input.demo.json`; n8n test inputs reproduced in Section 7.3 |
| Execution trace | **Local: saved; n8n: partially observed** | Saved local trace: `fixtures/trace.demo.json` (`n8n_executed: false`). n8n tool result and call count were observed interactively; full n8n trace and execution ID not archived here |
| Resulting output | **Observed** | Local file `fixtures/output.demo.json`; n8n chat outputs described in Section 7.3 |

### 7.1 Local deterministic implementation and proof

- **Implementation date:** 6 November 2026.
- **Local runtime:** Python standard library; local runner `scripts/restaurant_discovery.py`.
- **Original local workflow documentation:** `workflows/README.md`.
- **Local execution ID in the supplied proof file:** `local-b6306a15-4035-4d73-8e9f-b44874f426e9`.
- **Recorded local timestamp:** `2026-11-06T11:34:31Z` (UTC).
- **Input:** `fixtures/input.demo.json`.
- **Local trace:** `fixtures/trace.demo.json`.
- **Output:** `fixtures/output.demo.json`.
- **Reported local verification:** `python -m unittest discover -s tests -p "test_*.py" -v` → **10/10 tests passed**, independently rerun by the project author.
- **Observed data mapping:** `city=Heidelberg`, `cuisine=Greek`, `budget_max_eur=30` → catalog lookup over seven fictional restaurants → `demo-gr-01`.
- **Local limitations:** Deterministic rules, no LLM-driven reasoning, no conversation memory, no n8n or live availability. This remains a valid *local workflow proof*, not proof of autonomy.

### 7.2 Local acceptance checks

| Test | Local result | Evidence |
|---|---|---|
| T01: Greek restaurant in Heidelberg, ≤€30 | **PASS** | `demo-gr-01` returned; source and booking status preserved |
| T02: invalid/empty messages | **PASS** | Automated tests |
| T03: missing city | **PASS** | Requests clarification |
| T04: no exact cuisine match | **PASS** | Separately labeled alternatives |
| T05: unknown atmosphere | **PASS** | Does not invent atmosphere |
| T06: booking request | **PASS** | No confirmed reservation or availability claim |
| T07: unknown booking method | **PASS** | Retains `unknown` |
| T08: missing/broken catalog | **PASS** | Structured safe failure |
| T09: conversation memory | **NOT IMPLEMENTED LOCALLY** | Tested separately in n8n (Section 7.3) |
| T10: autonomous alternative-tool selection | **NOT IMPLEMENTED LOCALLY** | Tested separately in n8n (Section 7.3) |

### 7.3 Optional Step 6 — n8n AI Agent demonstration

**Test date:** 6 November 2026. **Environment:** Existing n8n instance accessed interactively (exact n8n version not recorded). **Model configured:** `gpt-4o-mini` via an OpenAI Chat Model node. **Evidence supplied:** Exported n8n workflow configuration, chat replies, one Code Tool output and an observed count of tool calls. **n8n execution ID and full downloaded execution trace:** not supplied.

**Export:** `workflows/ai_food_concierge_workflow.json` (sanitized for sharing; reconnect the OpenAI credential after importing).

**Configured workflow and connections:**

```text
When chat message received (Chat Trigger)
  -> AI Agent
     |-- OpenAI Chat Model (gpt-4o-mini)
     |-- Simple Memory (context window: 10)
     `-- Code Tool (JavaScript restaurant search over seven fictional records)
```

**Test N01 — Exact match and tool evidence (observed):**

- **Chat input:** `I'm looking for a Greek restaurant in Heidelberg with a budget of €30 per person.`
- **Chat output:** Recommended **Demo Greek Bistro**, Greek/Mediterranean, **€25 per person**.
- **Inspected Code Tool output:** `status=ok`, `data_mode=synthetic_demo`, `search={city:Heidelberg, cuisine:Greek, budget_max_eur:30}`, `match_count=1`, `matched_restaurants[0].restaurant_id=demo-gr-01`, `booking_channel=unknown`, `availability_checked=false`.
- **Result:** **PASS** for actual n8n input → agent-selected Code Tool → grounded chat output. The first chat reply omitted the fictional-data disclaimer, revealing a prompt/compliance issue.

**Test N10 — Autonomous alternative search (observed):**

- **Chat input:** `I'm looking for a Spanish restaurant in Heidelberg. If nothing matches, please suggest alternatives.`
- **Chat output:** No Spanish match reported; proposed **Demo Anatolia Table (€18)**, **Demo Mediterranean Kitchen (€22)** and **Demo Greek Bistro (€25)** as Mediterranean alternatives.
- **Agent execution log observation:** **Two Code Tool calls**, reported by the tester.
- **Result:** **Functional demonstration passed** for multi-call autonomous exploration. Individual per-call arguments and returned payloads were not preserved, so the exact alternative-search sequence is **not independently reconstructable** from this document.

**Test N09 — Conversation-memory continuity (observed):**

- **Follow-up in the same chat:** `Actually, I'd prefer Italian food instead. Keep my previous city.`
- **Chat output:** **Demo Pasta Corner**, Italian, **Heidelberg**, **€20 per person**.
- **Result:** **PASS at the chat-behavior level**: the assistant reused Heidelberg without the user repeating it and updated the cuisine. The separate internal memory state was not exported.

**Test N11 — Disclosure / fresh-session regression check (observed):**

- **Chat input (new session):** `I'm looking for Korean food in Heidelberg under €30.`
- **Chat output:** **Demo Seoul Kitchen**, Korean, Heidelberg, **€28**, including the explicit sentence: `Please note that all restaurant names and information are fictional demo data used for testing.`
- **Result:** **PASS** for grounded recommendation and explicit demo disclaimer after updating the system message. A Code Tool log for this particular new-session call was not separately supplied.

**Remaining limitations / operational risk:**

- All restaurant records are synthetic and embedded in the Code Tool; the workflow is not connected to a live restaurant database.
- No real-time table availability, booking execution, payments, external reservation integrations or production deployment were tested.
- The system prompt requests at most three tool calls, but no independent technical hard cap was demonstrated.
- Output disclaimers are prompt-driven; one initial response omitted the disclosure. A deterministic response guard would be more reliable for a public pilot.
- The complete n8n execution export/screenshot, execution ID, and per-call logs for the alternative search remain to be collected if stronger audit evidence is required.
- The sanitized workflow has no exported credentials or instance identifiers; credentials must be configured manually when imported into another n8n environment.

### 7.4 Submission checklist

- [x] Steps 1–5 documented with decisions, scope, assumptions and risks.
- [x] Local fallback implemented, tested, and saved with input/output/trace fixtures.
- [x] Optional n8n AI Agent configured and tested interactively with a fictional dataset.
- [x] n8n workflow exported; a sanitized copy supplied for sharing.
- [x] T01 exact-match search, T09 chat continuity, and T10 multiple tool calls observed in n8n.
- [x] Synthetic data clearly identified; no real booking or availability claims.
- [ ] Downloaded n8n execution trace / execution ID and full alternative-search per-call logs archived (not provided).

---

## 8. Conclusion

The AI Food Concierge is designed to reduce the effort of restaurant discovery through natural conversation and bounded autonomous exploration. Its first MVP focuses on the smallest differentiated experience that can be tested with reliable structured restaurant data in one city. Availability checks remain conditional on authorized access, while reservations, seating selection and delivery are later phases.

The planning work defines the business need, stakeholders, value proposition, technology decisions, MVP boundaries, risks, milestones, provisional resources, and evaluation measures. Optional Step 6 has additionally been demonstrated in n8n with a configured AI Agent, an observed search-tool response, a multi-call alternative search and a context-dependent follow-up. These observations are not evidence of production readiness, live availability or real reservations; the n8n execution ID and full machine-exported trace remain unarchived.
