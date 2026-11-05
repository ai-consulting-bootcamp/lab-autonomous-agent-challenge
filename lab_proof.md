# Lab Proof

## Step 1: Planning

**Project:** Customer Support Agent for a Logistics Company

| Goal | What the bot does | Success metric |
| --- | --- | --- |
| **Answer automatically** | Resolves customer questions from the company knowledge base and live shipment data | Deflection rate (share resolved without a human) |
| **Escalate complex issues** | Hands off to a human agent with the conversation summary attached | Escalation accuracy and first-response time |
| **Track history and satisfaction** | Logs every conversation and collects a CSAT rating | CSAT score, resolution rate |

**Why someone would pay:** It cuts cost per ticket and first-response time on high-volume “where is my order?” queries, while keeping humans on the high-risk cases.

```text
Customer → Channel (web/WhatsApp/email)
→ n8n webhook
→ Identity check → Intent routing
├─ FAQ/policy question  → LangChain RAG → ChromaDB → OpenAI
├─ "Where's my package?" → Tracking API → OpenAI formats answer
└─ Complex / angry / high-risk → Helpdesk ticket + Slack alert → human agent
→ Log to Postgres → CSAT survey → Dashboard
```

## Step 2: Technology Selection Framework

| # | Criterion | Does it apply? | Technology decision |
| --- | --- | --- | --- |
| 1 | **External knowledge base** | Yes. Answers must come from FAQs, shipping policies, and order/product information. | RAG with LangChain, Pinecone (vector store, embeddings, chunking), and OpenAI |
| 2 | **External systems** | Yes. The bot needs live order status and ticket creation. | API integrations (tracking, helpdesk), with LangChain handling retrieval |
| 3 | **Multi-step reasoning** | Yes. Different requests take different paths: FAQ, tracking, or escalation. | A structured n8n workflow with intent routing (LangGraph is the code-first alternative) |
| 4 | **Business systems** | Yes. The bot connects to the helpdesk, CRM, and database. | n8n as the orchestrator |
| 5 | **Autonomy level** | Partial. The bot acts on its own for routine questions, with a human in the loop for sensitive ones. | Escalation rules in n8n (see below) |

**Escalation triggers (criterion 5):**

- The customer asks for a person.
- Retrieval confidence is low.
- The topic is high-risk (claims, billing disputes, customs or legal issues).
- Sentiment is negative.
- The issue is unresolved after 2 to 3 turns.

### Technology Stack

| Layer | Choice |
| --- | --- |
| **Core LLM** | OpenAI |
| **RAG** | LangChain + ChromaDB |
| **Orchestration** | n8n |
| **Tracking** | Carrier or TMS API (or an aggregator like AfterShip or project44) |
| **Escalation** | Helpdesk (Zendesk or Freshdesk) + Slack or Teams alert |
| **History and CSAT** | PostgreSQL + in-chat rating |
| **Channel** | Web chat widget |
| Tools/integrations | See below |

### Tools & Integrations

| Integration | Purpose | Examples | Phase |
| --- | --- | --- | --- |
| **Order/shipment tracking API** | Live status, ETA, proof of delivery | Company TMS/WMS API, carrier APIs, or AfterShip/project44 | MVP |
| **Knowledge sources** | Feed the ChromaDB pipeline with FAQs, policies, and claims procedures | Google Drive, Confluence, Notion, PDFs | MVP |
| **Identity verification** | Confirm the customer before sharing shipment details | Tracking number + email/ZIP, checked against the order DB | MVP |
| **Helpdesk/ticketing** | Create a ticket with the conversation summary | Zendesk, Freshdesk | MVP |
| **Agent alerts** | Notify humans and enable live handoff | Slack or Teams | MVP |
| **Conversation store** | Log messages, intents, escalations, and CSAT | PostgreSQL | MVP |
| **Web chat widget** | Primary customer channel | Embedded chat connected to an n8n webhook | MVP |
| **CRM** | Customer profile and account tier for priority routing | HubSpot, Salesforce | Phase 2 |
| **Rates/quote API** | “How much to ship X to Y?” | Internal pricing service or carrier rates | Phase 2 |
| **WhatsApp / SMS / email** | Additional channels and status notifications | WhatsApp Business API, Twilio, Gmail | Phase 2 |
| **Analytics dashboard** | Deflection, escalation, CSAT, cost per ticket | Metabase, Looker Studio | Phase 2 |
| **LLM observability** | Trace prompts and retrieval quality | Langfuse, LangSmith | Phase 2 |

- **MVP:** RAG + tracking API + helpdesk escalation + Postgres logging.
- **Phase 2:** CRM, rates/quote API, WhatsApp, analytics dashboard, LLM observability (Langfuse).

## Step 3: MVP Scope

| **Must have (MVP)** | **Should-have (v2)** | **Nice-to-have** |
| --- | --- | --- |
| **Answer questions from knowledge base (RAG)**, with source citations and “I don’t know” fallback | **Multi-language support** (English plus the customer’s top 2 to 3 languages) | **Mobile app** (native in-app chat) |
| **Track order for a specific customer** via tracking API, after identity verification (tracking number + email/ZIP) | **CRM integration** (HubSpot/Salesforce) for customer profile, account tier, and VIP routing | **Voice support** (phone bot or voice notes) |
| **Helpdesk escalation**: ticket created with conversation summary, plus Slack/Teams alert to a human agent | **Multi-document types** (PDFs, scanned documents, spreadsheets, images such as damage photos) | **Proactive notifications** (delay alerts, delivery updates pushed to the customer) |
| **Escalation triggers**: customer asks for a person, low retrieval confidence, high-risk topic, negative sentiment, unresolved after 2 to 3 turns | **WhatsApp, SMS, and email channels** | **Self-service actions** (reschedule delivery, change address, file a claim) |
| **Conversation history logging** (PostgreSQL: messages, intents, escalation outcome) | **Rates/quote lookups** (“How much to ship X to Y?”) | **Sentiment-based agent coaching** and suggested replies for human agents |
| **CSAT survey** (1 to 5 rating after each chat) | **Analytics dashboard** (deflection, escalation rate, CSAT, cost per ticket) | **Customer personalization** based on shipping history |
| **Web chat widget** as the single channel | **LLM observability** (Langfuse/LangSmith) | **Admin UI** for non-technical staff to edit the knowledge base and escalation rules |
| **Basic guardrails**: PII handling, error fallback to human when an API is down | **Automated knowledge-base refresh** (scheduled re-ingestion, versioning) | **Multi-tenant setup** to resell to other logistics companies |

## Step 4: Assess Risks and Mitigation

### Technical risks

| Risk | Description (what could go wrong) | Probability | Impact | Mitigation strategy |
| --- | --- | --- | --- | --- |
| **Wrong chunks retrieved** | The retriever returns irrelevant or outdated passages, so the bot gives inaccurate answers. | Medium | High | Tune chunking (about 500 to 800 tokens with overlap, split by section). Use hybrid search (keyword + vector) with a reranker. Add metadata filters (document type, date). Set a similarity threshold below which the bot says “I don’t know” and escalates. Show source citations. Maintain a golden test set of real questions and run it after every change. |
| **API rate limits or cost** | OpenAI or tracking API limits are hit during peak volume, or token costs exceed budget. | Medium | Medium | Cache frequent answers and tracking lookups. Queue requests in n8n and apply rate limiting. Use a smaller model for routing and a larger one only for generation. Set token limits per conversation, monthly spend caps, and usage alerts. |
| **Integration failure** | The tracking API, helpdesk, or database goes down or returns bad data. | Medium | High | Set timeouts, retries with exponential backoff, and a circuit breaker. If the tracking API fails, tell the customer honestly and create a ticket automatically instead of guessing. Monitor integration health with alerts. |
| **LLM model failure** | OpenAI has an outage, degraded quality, or a model version change that alters behavior. | Medium | High | Add a fallback LLM (such as Anthropic or Gemini) through an n8n error branch. Keep prompts portable and pin model versions. If both fail, hand off to a human. |
| **Performance issues** | Slow responses (retrieval + LLM + API calls in sequence) frustrate customers, and the system degrades under load. | Medium | Medium | Set a target of under 5 s for the first response. Stream answers, cache FAQs, and run independent calls in parallel. Run n8n in queue mode and load-test before launch. |
| **Hallucination / prompt injection** *(added)* | The bot invents an ETA or claim policy, or a customer manipulates it into revealing data or ignoring rules. | Medium | High | Answer only from retrieved context or API data. Validate tracking data and verify identity before any disclosure. Add input and output guardrails. Never let the LLM make claim or refund decisions. |

### Business risks

| Risk | Description (what could go wrong) | Probability | Impact | Mitigation strategy |
| --- | --- | --- | --- | --- |
| **User adoption** | Customers don’t trust the bot or keep asking for a human, so deflection stays low. | Medium | High | Make the first answers useful (tracking is the top query). Offer a visible “talk to a person” option. Launch with a pilot group, track deflection and CSAT weekly, and improve the top failing intents. |
| **Change management** | Support agents fear replacement or resist the new handoff process, and handoffs lose context. | Medium | Medium | Position the bot as handling repetitive tickets so agents focus on complex ones. Train agents on the handoff flow. Include the conversation summary in every ticket and collect agent feedback. |
| **Cost overruns** | Build, LLM usage, and infrastructure costs exceed the savings per ticket. | Medium | Medium | Build a cost-per-conversation model before launch and compare it with cost per human ticket. Track actual spend weekly. Use smaller models where possible and keep to the MVP scope. |
| **Scope creep** | Stakeholders keep adding features (languages, CRM, WhatsApp), which delays launch. | High | Medium | Freeze the Step 3 MVP list. Route new requests to the v2 backlog with a written priority decision. Use the test: “Does the bot still resolve, escalate, and log without it?” |
|  |  |  |  |  |

### Data risks

| Risk | Description (what could go wrong) | Probability | Impact | Mitigation strategy |
| --- | --- | --- | --- | --- |
| **Data quality** | The knowledge base is outdated, contradictory, or poorly formatted (scanned PDFs, duplicate policies), so the bot gives wrong answers. | High | High | Audit and clean documents before ingestion. Assign an owner per document set. Schedule re-ingestion and version documents. Remove superseded policies. |
| **Privacy / security** | Customer names, addresses, and shipment details leak or are sent to the LLM unnecessarily. | Medium | High | Verify identity before sharing shipment data. Redact PII before LLM calls. Encrypt data in transit and at rest and apply role-based access. Set retention limits. Comply with GDPR/CCPA and review the LLM provider’s data-use terms. |
| **Data availability** | The tracking API has gaps or delays, or key documents are scattered across systems and not accessible. | Medium | Medium | Map data sources and confirm API access early. Show “last updated” times on tracking data. Escalate when data is missing instead of guessing. |
| **Bias in training data** | The LLM or knowledge base performs unevenly across languages, regions, or customer types, or favors certain customers in tone or resolution. | Low | Medium | Test the golden set across customer segments and phrasing styles. Use a consistent system prompt and policy rules. Review escalation and CSAT rates by segment. Add languages only after testing them. |

## Step 5: Project Plan

### Implementation Phases

| Phase | Goal | Key activities | Deliverables |
| --- | --- | --- | --- |
| **1. Setup and data preparation** | Environment ready and clean knowledge base ingested | Set up n8n, PostgreSQL, ChromaDB, and the OpenAI account. Confirm access to the tracking and helpdesk APIs. Audit and clean the FAQs, policies, and claims documents. Build the chunking, embedding, and ingestion pipeline. Create the golden test set (about 100 real questions). | Working environments, indexed knowledge base, golden set, API access confirmed |
| **2. Core agent development** | The bot answers, tracks, and escalates in isolation | Build the RAG chain (LangChain + ChromaDB + OpenAI) with citations and an “I don’t know” threshold. Build n8n intent routing (FAQ, tracking, escalation). Add identity verification and the tracking API tool. Implement the escalation triggers. Write the system prompt and guardrails. | Working RAG bot, routing workflow, escalation logic |
| **3. Integration and testing** | End-to-end system works and meets quality targets | Connect the helpdesk ticket and Slack/Teams alert. Add PostgreSQL logging and the CSAT survey. Embed the web chat widget. Run the golden set, tune retrieval, and fix gaps. Test failure paths (API down, LLM down), prompt injection, and load. Run a privacy and security review. | Integrated system, test report, security sign-off |
| **4. Deployment and monitoring** | Safe launch and continuous improvement | Run a shadow-mode pilot (bot drafts, humans send), then 10% of traffic, then full rollout. Set up dashboards and alerts for cost, latency, errors, and CSAT. Train support agents on handoff. Define the rollback plan and the weekly review. |  |

### Timeline

Estimated MVP duration: **about 12 weeks**.

| Phase | Duration | Weeks | Key milestone |
| --- | --- | --- | --- |
| 1. Setup and data prep | 3 weeks | 1 to 3 | **M1:** Knowledge base indexed and golden set approved |
| 2. Core agent development | 4 weeks | 4 to 7 | **M2:** Bot passes the internal demo (answer, track, escalate) |
| 3. Integration and testing | 3 weeks | 8 to 10 | **M3:** Meets accuracy and latency targets on the golden set |
| 4. Deployment and monitoring | 2 weeks, then ongoing | 11 to 12 | **M4:** Pilot live, then full rollout |

### Dependencies

| Dependency | Needed by | Risk if late |
| --- | --- | --- |
| Tracking API access and credentials | Week 2 | Blocks the tracking feature and Phase 2 |
| Helpdesk (Zendesk/Freshdesk) sandbox | Week 5 | Delays escalation testing |
| Cleaned, owner-approved knowledge documents | Week 3 | Poor retrieval quality and a rework loop |
| Legal/privacy approval (data sent to the LLM) | Week 6 | Blocks launch |
| Support team availability for the golden set and pilot | Weeks 2 and 11 | Weak test coverage, low adoption |
| Phase 2 complete before Phase 3 | Week 8 | Phases are sequential, so slips push the launch date back |

### Team and roles

| Role | Responsibility | Commitment |
| --- | --- | --- |
| **Product owner / project manager** | Scope control, stakeholder alignment, success metrics | Part-time |
| **AI/LLM engineer** | RAG pipeline, prompts, guardrails, evaluation | Full-time |
| **Integration engineer (n8n)** | Workflows, API, helpdesk, and database integration | Full-time |
| **Data/knowledge engineer** | Document cleanup, ingestion, KB refresh process | Part-time |
| **QA engineer** | Golden set, regression, load, and failure testing | Part-time (Phases 3 to 4) |
| **DevOps** | Hosting, backups, monitoring, CI/CD | Part-time |
| **Support team lead (domain expert)** | Validates answers, escalation rules, and agent training | Part-time |
| **Security/privacy reviewer** | PII handling, GDPR/CCPA, LLM data terms | Ad hoc |

### Tools and services

| Category | Tools |
| --- | --- |
| **AI** | OpenAI API (plus a fallback LLM), LangChain, ChromaDB (move to Qdrant/pgvector for production) |
| **Orchestration** | n8n (self-hosted in queue mode, or n8n Cloud) |
| **Data** | PostgreSQL (history, CSAT, logs) |
| **Integrations** | Tracking API (TMS or carrier/aggregator), Zendesk/Freshdesk, Slack/Teams |
| **Ops** | Cloud hosting (AWS/GCP/Azure), Langfuse (observability), Metabase (dashboard), secrets manager |

### Budget considerations

| Item | Type | Notes |
| --- | --- | --- |
| **Team labor** | One-time, largest cost | About 3 to 4 FTE-equivalents over 12 weeks |
| **LLM usage** | Variable | Depends on conversation volume and model choice. Estimate cost per conversation and set monthly caps. |
| **Cloud infrastructure** | Monthly | n8n, database, and vector store hosting, plus backups |
| **Third-party APIs and licenses** | Monthly | Tracking aggregator, helpdesk seats, n8n license or cloud plan |
| **Monitoring and security** | Monthly/one-time | Observability tool, security review, penetration test |
| **Contingency** | One-time | Reserve 15 to 20% for overruns, per the cost-overrun risk in Step 4 |
|  |  |  |

- Budget check: compare total monthly run cost with (tickets deflected × cost per human ticket). The bot has to come out clearly cheaper to be worth paying for.
