# LAB | Architect the Bot Someone Will Actually Pay For (`lab_proof.md`)

---

## Executive Summary: Prompt Discipline & Verification

### 1. Three Workflow Risks
1. **Misclassification of Billing vs. Refund Emails (Technical / Routing Risk):** If the classifier mislabels a double-charge billing complaint as a standard shipping or return request, the downstream RAG step retrieves the wrong policy document and drafts a polite but useless reply.
2. **Policy Hallucination on Edge Cases (Technical / Faithfulness Risk):** When a customer requests a partial refund on a multi-item bundle or reports health/safety damage, the LLM may invent return window exceptions not present in the company's PDF policy.
3. **Uncontrolled Scope Creep & Premature Write-Access (Business / Operational Risk):** Stakeholders may push to connect the agent directly to payment gateways (Stripe/Shopify) to issue instant refunds or expand into Spanish and WhatsApp before the core English email drafting pipeline hits its quality threshold.

### 2. Two Trace Checks
1. **Classification & Routing Gate Check (`node: classify_intent`):** Verify that `intent_category == "refund_request"`, `confidence_score >= 0.85`, and `is_multi_item_edge_case == false` before allowing the workflow to proceed to automated policy synthesis; otherwise, verify that the trace branches to `human_escalation_queue`.
2. **RAG Groundedness / Citation Check (`node: retrieve_policy_chunks` & `node: draft_response`):** Verify that `retrieved_chunk_ids` is non-empty (top-$k$ similarity score $\ge 0.78$) and that the output payload includes an explicit `policy_citation` matching the retrieved document section (e.g., `Return_Policy_2026_v1.pdf#Section-3.2`).

### 3. One Simplification
* **Smallest Useful Version (Read-Only Human-in-the-Loop Drafts for Standard Single-Item Refunds):** Instead of building a full end-to-end autonomous agent that handles all 500 daily emails across shipping, complaints, and billing and executes live refunds in the ERP/payment system, we restrict the MVP to **one narrow critical path**: classifying incoming emails, retrieving the official PDF refund policy for single-item refund requests, and saving a cited draft reply in the helpdesk for a human agent to review and send. Tricky cases (multi-item orders, damaged goods) are automatically flagged for manual handling.

### 4. Verification: Execution Evidence
* **Execution Evidence Named:** The workflow execution is proven by trace ID `trc_9f82a104-7c3b-4e91-b12d-88e4019a2c11` (timestamp `2026-11-11T09:42:11.402Z`), which records the state transition across three nodes (`classify_email` $\rightarrow$ `retrieve_refund_policy` $\rightarrow$ `generate_draft_output`), consumes $642$ total tokens across a two-tier model call, verifies retrieval of chunk `pol_chk_042` (`similarity: 0.89`), and writes the verified output record `out_rec_20261111_0089` with status `READY_FOR_HUMAN_REVIEW`.

---

# Autonomous Agent Project Plan

## 1. Use Case

### Selected Option
**Option A: Customer Support Agent (Scoped to E-Commerce Refund Triage & Draft Generation)**

### Problem Statement
An online retail shop receives approximately $500$ customer support emails per day covering order tracking, complaints, billing issues, and refund requests. Support agents spend hours manually reading emails, looking up return window rules in internal policy PDFs, checking order eligibility, and typing repetitive responses. This backlog causes response delays of up to $48\text{ hours}$ and inconsistent policy enforcement.

### Target Users
* **Primary Users:** Customer Support Representatives (CSRs) and Support Team Leads who review and send AI-generated draft replies inside their ticketing inbox.
* **Indirect Beneficiaries:** End customers who receive faster, policy-accurate responses to their refund inquiries.

### Verification Criteria (How We Know It's Working)
We know the system is working when:
1. At least $90\%$ of incoming refund emails are classified into the correct category (`refund_standard`, `refund_edge_case`, or `non_refund`).
2. Drafted replies achieve a **Faithfulness (Groundedness)** score of $\ge 0.90$ against the official Refund Policy PDF on a golden test set of $50$ historical emails.
3. Average human handling time (reading + checking + sending) drops from $8\text{ minutes}$ per refund email to under $90\text{ seconds}$ (accounting for human checking time).

### Current Manual Process
1. A customer sends an email to `support@shop-example.com`.
2. A support agent opens the ticket, reads the text, and determines whether it is a refund request, shipping question, or billing dispute.
3. The agent opens a shared Google Drive folder, searches the `Return_and_Refund_Policy.pdf` document to verify rules (e.g., $30\text{-day}$ window, unopened condition, restocking fees).
4. The agent manually types a response from scratch or copies a rough template, edits the details, and sends the email.

### Alignment with the Four Key Questions (Course Framework)
1. **What type of problem is this?**
   * It is a combination of **Classification** (sorting emails into refund vs. billing/shipping/complaint, which is the critical step—since a great reply to the wrong category is useless), **Ranking** (scoring and retrieving the top-$k$ relevant policy chunks via RAG), and **Generation** (drafting a polite, grounded response).
2. **How do we measure success: quality or quantity?**
   * **Hybrid (Quantity with a Quality Gate via Human-in-the-Loop):** Processing $500$ emails/day is a quantity bottleneck, but promising a refund when company policy forbids it costs money. Therefore, the AI optimizes for speed by generating rapid first drafts, while a human checks the draft in $15\text{--}30\text{ seconds}$ before sending ("Solution 2: Custom pipeline with human-in-the-loop").
3. **Where is the data, what is it, and when do we get it?**
   * **Data Maturity: Medium-to-Low.** Historical emails exist in the helpdesk, and the refund policy exists as a PDF, but historical tickets are inconsistently tagged ("a train can hide another train"—some old emails reflect outdated holiday return policies). We include buffer time in Phase 1 to clean and construct a $50\text{-example}$ Golden Test Set.
4. **Does it need to keep improving over time?**
   * **Yes.** Product lines, seasonal return windows, and customer phrasing change over time (data drift). The system requires a 4-part continuous improvement loop: **Feedback Collection** (tracking whether agents edit or reject drafts), **Drift Detection** (monitoring weekly acceptance rates), **Retraining/Prompt Updating** (updating the RAG knowledge base when new products launch), and **Rollback** (versioning prompts and vector indices).

---

## 2. Technology Stack

### Technology Selection Framework Questionnaire
1. **Does it need external knowledge?**
   * **Yes $\rightarrow$ Needs RAG.** The LLM cannot know the shop's specific return window, restocking fees, or non-refundable item list without retrieving from internal policy documents.
2. **Does it need to interact with external systems?**
   * **Yes $\rightarrow$ Needs tools/integrations.** It must ingest ticket payloads and write draft responses back to the helpdesk/review queue.
3. **Does it need multi-step reasoning?**
   * **Yes $\rightarrow$ Consider LangGraph for structured workflows.** The agent must first classify intent and detect edge cases, conditionally decide whether to retrieve policy chunks or escalate immediately, and then synthesize a grounded response.
4. **Does it need to integrate with business systems?**
   * **Yes $\rightarrow$ n8n (or webhook orchestration) for business system triggers.** In production, n8n connects the email inbox/Zendesk webhook to the Python LangGraph service.
5. **Does it need to be autonomous (run without human input)?**
   * **Yes (Event-driven with Human-in-the-Loop).** It triggers automatically upon email arrival without a human clicking "run," requiring error handling, retry logic, and LangSmith monitoring, though final dispatch requires human approval.

### Documented Technology Stack
* **Core LLMs (Tiered Cost Strategy):**
  * *Classifier & Router Node:* `gpt-4o-mini` (OpenAI) — fast, low-latency, and inexpensive for structured JSON classification.
  * *RAG Synthesis & Drafting Node:* `gpt-4o` (OpenAI) or `claude-3-5-sonnet` (Anthropic) — high instruction-following and faithfulness for policy-grounded customer communication.
* **RAG Components:**
  * *Embeddings:* OpenAI `text-embedding-3-small`.
  * *Vector Database:* ChromaDB (local/lightweight for PoC/MVP) migrating to Qdrant or pgvector in production.
  * *Chunking Strategy:* Recursive character text splitting (`chunk_size = 500` tokens, `chunk_overlap = 75` tokens) preserving markdown section headers so policy citations remain intact.
* **Agent Framework:**
  * **LangGraph (Python):** Provides deterministic state-machine control over the `Classify` $\rightarrow$ `Route` $\rightarrow$ `Retrieve` $\rightarrow$ `Draft` nodes with strict Pydantic schema validation.
* **Orchestration:**
  * **n8n:** Handles the email webhook trigger, payload normalization, rate-limit queuing, and posting the final JSON output back as an internal helpdesk draft note.
* **Tools & Integrations:**
  * Helpdesk API (Zendesk / Freshdesk mock webhook for MVP), ChromaDB Retriever Tool, and LangSmith for execution tracing.

### Justification, Alternatives, and Trade-Offs
* **Why this stack (Solution 2 Architecture):** Referring to the course notes' comparison of *Solution 1 (Prompt + n8n)*, *Solution 2 (Custom Pipeline with RAG + Human-in-the-Loop)*, and *Solution 3 (Self-improving autonomous system)*, Solution 2 is the optimal starting point. Solution 1 treats all $500$ emails identically and stuffs the entire policy into one prompt, which breaks as policies grow. Solution 3 is over-engineered and too expensive before proving business value.
* **Alternatives Considered:**
  * *Pure n8n + Single LLM Node (Solution 1):* Faster to build ($1\text{--}2\text{ days}$), but lacks deterministic state routing, structured RAG evaluation, and modular unit testing.
  * *Autonomous ReAct Agent (Unconstrained LangChain Agent):* Too unpredictable; an unconstrained loop might call tools repeatedly, driving up token costs and latency. LangGraph's directed cyclic/acyclic graph enforces strict boundaries.
* **Trade-Offs:** Maintaining both an n8n trigger layer and a Python LangGraph service introduces deployment overhead compared to a no-code flow, but it buys strict type safety, lower per-token cost via model tiering, and verifiable execution traces.

---

## 3. MVP Scope

### Feature Brainstorming & Categorization

| Category | Features |
| :--- | :--- |
| **Must-Have (MVP)** | • Single-language support (English emails only)<br>• Intent classification (`refund_standard`, `refund_edge_case`, `other`)<br>• RAG over a single official PDF (`Return_Policy_2026_v1.pdf`)<br>• Grounded draft generation with explicit policy section citations<br>• Edge-case flagging (multi-item orders, partial refunds, damaged items routed to human)<br>• Human-in-the-loop output (creates internal draft, never auto-sends to customer)<br>• Execution trace logging for every run |
| **Should-Have (v2)** | • Read-only Shopify/Order DB lookup tool to verify purchase date automatically<br>• Automated LLM-as-a-judge faithfulness scoring in CI/CD<br>• Coverage for "Where is my order?" (shipping status) emails<br>• Feedback capture button in helpdesk (thumbs up/down on AI drafts) |
| **Nice-to-Have (v3+)** | • Multi-language support (Spanish, German)<br>• Omnichannel intake (WhatsApp, Instagram DMs)<br>• Automated refund execution in Stripe/Shopify for orders under $\$25$<br>• Automated weekly drift detection & retraining pipeline (Solution 3) |

### MVP Boundaries
* **What is Included:**
  * Automated ingestion of an incoming customer email payload (JSON).
  * Multi-step LangGraph workflow: Classification $\rightarrow$ Conditional Check $\rightarrow$ PDF Vector Retrieval $\rightarrow$ Draft Reply Generation.
  * Structured output record containing the classification, retrieved policy citation, confidence flag, and draft email text.
* **What is Explicitly Out of Scope (Excluded):**
  * **No Direct Financial Execution:** Following the production rule *"On a company's first AI project, don't touch systems that bring in money (orders, invoices, accounting),"* the agent has **zero write access** to payment processors or ERP systems.
  * **No Auto-Sending:** No email is ever sent directly to a customer without a human clicking "Send."
  * **No Multi-Language or Non-Email Channels:** Spanish and WhatsApp requests are deferred to Phase 2+.
* **Managing Scope Creep:** Any stakeholder request for new languages or channels during the build will be answered with a visible cost/timeline trade-off: *"Adding Spanish support requires a translated golden test set and adds $2\text{ weeks}$ to the timeline—should we push the launch date or log it for Phase 2?"*

---

## 4. Risk Assessment

### Technical, Business, Data, and Legal Risks

| Risk Category | Risk Description | Prob. | Impact | Mitigation Strategy |
| :--- | :--- | :---: | :---: | :--- |
| **Technical (Workflow Risk 1)** | **Misclassification of Email Intent:** A billing error ("charged twice") is misclassified as a standard product return, resulting in an irrelevant reply. | Medium | High | Use structured JSON output with few-shot examples in the classifier prompt; route any classification with confidence $< 0.85$ to `MANUAL_TRIAGE`. |
| **Technical (Workflow Risk 2)** | **Model Hallucination on Edge Cases:** The LLM invents refund eligibility rules for multi-item bundles or damaged goods not covered in the retrieved chunks. | Medium | High | Strictly instruct the system prompt to answer *only* from retrieved context; explicitly flag multi-item or partial-refund requests for human handling ($80/20$ rule). |
| **Technical** | **High API Costs from Token Spikes:** Verbose email threads or runaway agent loops inflate monthly LLM bills. | Low | Medium | Split the task across model tiers (`gpt-4o-mini` for sorting, `gpt-4o` only for verified standard refund drafting); truncate email history to the latest $1,000\text{ words}$; set hard OpenAI spend alerts. |
| **Business (Workflow Risk 3)** | **Scope Creep & Unclear Value:** Stakeholders demand WhatsApp, Spanish, and automated CRM updates mid-sprint, delaying launch and blowing the budget. | High | High | Enforce strict MVP boundaries in the project charter; price every change request in weeks/euros and defer to Phase 2. |
| **Business** | **Low User Adoption / Checking Fatigue:** Support agents distrust the AI drafts or spend longer fixing bad drafts than writing from scratch. | Medium | High | Co-design the Golden Test Set with senior support agents; format outputs with clear bulleted policy citations so checking takes $< 20\text{ seconds}$. |
| **Data** | **"A Train Hiding Another Train" (Hidden Data Messiness):** Policy PDFs contain conflicting rules from old seasonal promotions, causing contradictory RAG answers. | Medium | High | Audit and standardize the single source-of-truth PDF in Phase 1 before indexing; separate knowledge bases by use case rather than dumping all company docs into one vector store. |
| **Data / Legal** | **Privacy, GDPR & EU AI Act Compliance:** Customer emails contain PII (names, addresses, phone numbers, order IDs) sent to external LLM APIs; EU AI Act transparency rules apply. | High | High | Strip or mask unnecessary PII (credit card numbers, phone numbers) before LLM calls; use zero-data-retention enterprise API endpoints; include clear disclosure and human sign-off on all external communications. |

---

## 5. Implementation Plan

### Project Phases & Timeline (Total Duration: 6 Weeks)

```
Week 1          Week 2          Week 3          Week 4          Week 5          Week 6
[--- Phase 1 ---][----- Phase 2 -----][------ Phase 3 ------][--- Phase 4 ---]
Data & Audit     PoC & Core MVP       Testing & Evaluation   Deploy & Monitor
```

#### Phase 1: Setup, Data Audit, and Golden Test Set (Week 1 — 40 Hours)
* **Activities:** Audit `Return_Policy_2026_v1.pdf` to remove outdated clauses; sample $100$ historical support emails (including $20\%$ edge cases); collaborate with the client's Support Lead to label a $50\text{-question}$ Golden Test Set. Add buffer time for cleaning messy email threads.
* **Milestone 1:** Signed-off single source-of-truth PDF and labeled $50\text{-item}$ Golden Test Set JSON.
* **Dependencies:** Access to anonymized historical helpdesk tickets and $2\text{ hours}$ of the Support Lead's calendar.

#### Phase 2: PoC and Core Agent Development (Weeks 2–3 — 60 Hours)
* **Activities:**
  * *Week 2 (PoC):* Build the minimal Python prototype (1 PDF in ChromaDB + 3-node LangGraph workflow triggered manually) and test against $10$ sample emails to verify the critical path.
  * *Week 3 (MVP Core):* Implement the multi-item edge-case detector, tiered LLM calls (`gpt-4o-mini` + `gpt-4o`), and structured Pydantic output schemas.
* **Milestone 2:** Working LangGraph service passing end-to-end execution traces locally.
* **Dependencies:** OpenAI API keys, LangSmith project setup.

#### Phase 3: Integration and Quality Evaluation (Weeks 4–5 — 50 Hours)
* **Activities:** Connect n8n webhook to ingest helpdesk emails and post internal draft notes; run automated evaluation using Ragas/DeepEval and an independent **LLM-as-a-judge** (using Anthropic Claude to grade OpenAI's outputs so grades are not overly generous); conduct human review on edge cases.
* **Milestone 3:** System hits $\ge 90\%$ classification accuracy and $\ge 0.90$ faithfulness on the Golden Test Set.
* **Dependencies:** Staging helpdesk sandbox environment.

#### Phase 4: Deployment, Handover, and Monitoring Setup (Week 6 — 30 Hours)
* **Activities:** Deploy to production for $100\%$ of incoming refund emails in draft-only mode; configure daily cost alerts and weekly drift detection dashboards; train support team on reviewing drafts; formalize maintenance ownership agreement.
* **Milestone 4:** Production Go-Live and Maintenance Handover Sign-Off.

### Resources Needed
* **Team Members & Roles:**
  * **AI Consultant (Lead — $0.5\text{ FTE}$):** Owns problem scoping, business alignment, Golden Test Set curation with client experts, scope creep management, and quality evaluation.
  * **AI Engineer ($1.0\text{ FTE}$ during Weeks 2–5):** Builds the LangGraph state machine, ChromaDB chunking pipeline, n8n webhook integrations, and PII masking middleware.
  * **Client Domain Expert (Support Team Lead — $2\text{ hrs/week}$):** Defines what a "good" refund answer looks like and reviews Golden Test Set edge cases.
* **Tools & Services:** OpenAI API (Enterprise/Zero-Retention), Anthropic API (for independent LLM-as-a-judge evaluation), LangSmith (trace observability), n8n (self-hosted or cloud starter), ChromaDB.
* **Budget Considerations:**
  * **Estimated Build Cost:** $\sim 180\text{ hours}$ blended consulting/engineering effort.
  * **Estimated Monthly Running Cost (for $500\text{ emails/day} = 15,000\text{ emails/month}$):**
    * Classification (`gpt-4o-mini` @ $15,000$ calls): $\approx \$3.50/\text{month}$
    * RAG Drafting (`gpt-4o` @ $\sim 8,000$ standard refund calls): $\approx \$45.00/\text{month}$
    * Hosting & n8n/LangSmith observability: $\approx \$100.00/\text{month}$
    * **Total Run Rate:** $\approx \$148.50/\text{month}$ (delivering $\sim 35\text{ hours/month}$ of saved support labor).

---

## 6. Success Metrics

We evaluate the MVP using a combination of **RAG Quality Metrics**, **Agent Step Metrics**, and **Business Quantity/Efficiency Metrics** (setting realistic $90\%$ targets rather than chasing an impossible $100\%$):

### 1. RAG Evaluation Metrics (Evaluated via Ragas + Independent LLM-as-a-Judge)
* **Context Precision ($\ge 0.85$):** Proportion of retrieved policy chunks that are genuinely relevant to the customer's refund question vs. noise.
* **Context Recall ($\ge 0.90$):** Ability of the retriever (at $k = 3$) to find all policy clauses needed to answer the query.
* **Faithfulness / Groundedness ($\ge 0.90$):** Every factual claim in the draft reply must be backed by the retrieved policy chunk:
  $$\text{Faithfulness} = \frac{\text{Number of Claims Supported by Retrieved Context}}{\text{Total Number of Claims in Draft Reply}} \ge 0.90$$
* **Answer Relevance ($\ge 0.90$):** How well the generated draft directly addresses the customer's specific question without tangential filler.

### 2. Agent Step & Routing Metrics (Evaluated via LangSmith Traces)
* **Intent Classification Accuracy ($\ge 90\%$):** Percentage of incoming emails routed to the correct branch (`refund_standard`, `refund_edge_case`, `non_refund`).
* **Edge-Case Escalation Recall ($\ge 95\%$):** Percentage of multi-item orders, partial refund requests, or damaged-goods claims successfully flagged for `HUMAN_ESCALATION` rather than auto-drafted as standard returns.
* **Tool Call Accuracy ($100\%$):** Percentage of vector store queries executed with valid schema parameters and zero unhandled exceptions.

### 3. Business & Operational Metrics ( Accounting for Checking Time)
* **Net Time Saved per Ticket:** Target reduction from $8.0\text{ minutes}$ (manual lookup + typing) to $1.5\text{ minutes}$ ($0.1\text{ min}$ AI generation + $1.4\text{ min}$ human verification and send), yielding a net savings of $6.5\text{ minutes}$ per standard refund ticket.
* **Draft Acceptance Rate ($\ge 80\%$):** Percentage of AI-generated drafts sent by support agents with zero or minor cosmetic edits.
* **Drift Threshold (Post-Launch Watch):** If the weekly Draft Acceptance Rate drops below $75\%$, a drift alert triggers a review of newly introduced store products or policy updates.

---