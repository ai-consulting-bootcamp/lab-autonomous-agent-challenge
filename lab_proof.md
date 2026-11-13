# Autonomous Agent Project Plan
## Procurement Risk & Mitigation Agent

**Lab:** Architect the bot someone will actually pay for  
**Company:** Bakery Foods Inc. (fictional French bakery manufacturer)  
**Business function:** Raw Materials Procurement  
**Deliverable:** Autonomous Agent Project Plan  
**Project status:** Proposed solution; business assumptions and technical design require validation

## 1. Use Case

### Business problem
Bakery manufacturers depend on agricultural ingredients exposed to price volatility and supply disruptions. Procurement managers must connect external market developments with supplier contracts and demand forecasts to determine whether mitigation is warranted.

**Decision to support:** Which developments matter to our ingredients, what is our exposure, and what mitigation options should we investigate?

The current process is assumed to involve manual review of market sources, supplier/contract information, forecasts, and procurement policies before preparing an assessment. Its actual time burden and error rate have **not** been measured for this fictional company. This workflow and its pain points require validation with procurement users.

### Proposed solution and target user
An **on-demand Procurement Risk Assessment & Mitigation Agent** for a Raw Materials Procurement Manager. The manager enters an ingredient and assessment horizon (e.g., sunflower oil for three months). The system gathers relevant external evidence and synthetic internal records, computes transparent exposure scenarios, and produces a reviewable Procurement Risk Assessment & Mitigation Strategy Report.

The report includes an executive summary, risks and supporting sources, supplier exposure, scenario-based financial impact, mitigation options, uncertainties, and decisions requiring approval.

The system **does not** approve suppliers, place orders, change contracts, or make purchasing commitments. Procurement managers retain those decisions.

### Why agentic capabilities?
External research can be incomplete or contradictory. The proposed agent assesses evidence gaps and may select another targeted research action, subject to explicit time, tool-call, and iteration limits. This is a candidate justification for **stateful, adaptive research**, not a claim that every task needs AI. Structured record retrieval, financial calculations, validation, and approvals remain deterministic or human-controlled.

### Value hypothesis and verification
The intended value is less first-pass research preparation effort and more consistent, traceable risk assessments. These benefits are hypotheses, not measured outcomes. Prototype verification would focus on whether the research-to-report workflow functions correctly; business value requires later user testing and baseline comparisons.

## 2. Technology Stack

| Component | Proposed technology | Requirement and rationale |
|---|---|---|
| Core language model | OpenAI API | Interpret requests and evidence, identify research gaps, and draft grounded report sections; not the authority for numerical calculations |
| Agent framework | LangGraph with Python | Maintain research state, choose tools conditionally, loop when evidence is incomplete, and enforce explicit stopping conditions |
| Workflow integration | n8n | Receive a form/webhook request, call the agent service, route completion/failure status, and deliver the report; not a second reasoning engine |
| Structured data | Supabase PostgreSQL | Query synthetic suppliers, contracts, and forecasts as structured records |
| Document retrieval | PostgreSQL + pgvector, document chunks, OpenAI embeddings | Retrieve relevant passages from fictional procurement policies and supplier documents |
| Financial calculations | Python functions | Produce reproducible scenario calculations from validated inputs and labeled assumptions |
| External research | Candidate commodity data, news, and web-search integrations | Retrieve dated, attributable market evidence; source suitability and access still require checking |
| Optional interoperability | One MCP-connected research tool | Demonstrate standardized tool access only if it adds value after the core path works |

**Candidate external sources:** World Bank Pink Sheet, GDELT, and Tavily. Coverage, recency, pricing, and suitability for sunflower oil have **not** been verified in the project documents.

### Alternatives and trade-offs
- **Simple Python workflow vs. LangGraph:** A fixed sequence or Python loop could be cheaper and easier to maintain. LangGraph is justified only if conditional research decisions and explicit state management materially improve the workflow. Its costs are additional implementation and testing complexity.
- **n8n vs. Python-only integration:** Python alone could handle request and delivery. n8n offers a visible business-system integration layer but adds a service and failure point.
- **pgvector/RAG vs. direct document lookup:** For a small fictional document set, direct lookup or prompt-provided context may suffice. Keep pgvector only if semantic retrieval is useful and can be evaluated.
- **AI vs. deterministic logic:** Use AI for interpreting ambiguous evidence and drafting. Use SQL and Python for exact records, formulas, and validation. Human review is required for consequential procurement choices.

### Proposed flow
1. **Trigger:** Procurement manager submits ingredient and horizon through n8n.
2. **Validate:** Required fields and permitted values are checked.
3. **Research:** LangGraph calls external research tools, reviews evidence, and may investigate specific gaps within a bounded loop.
4. **Retrieve:** Read-only SQL obtains contracts, suppliers, and forecasts; document retrieval obtains relevant policies.
5. **Calculate:** Python computes exposure scenarios only when required inputs are available.
6. **Assemble and validate:** The system produces a sourced report, labels assumptions, and flags unresolved uncertainty.
7. **Deliver:** n8n sends the report or a clearly identified failure/partial-result notification.
8. **Human decision:** Procurement manager reviews options and authorizes any next action outside the agent.

If sources conflict, the agent first checks whether they describe comparable regions, periods, and measures. It may perform targeted follow-up research when the disagreement is material and the research budget permits. If unresolved, it reports the conflict rather than fabricating certainty.

## 3. MVP Scope

### Must-have (MVP)
- One ingredient end-to-end: **sunflower oil**.
- On-demand input specifying ingredient and assessment horizon.
- Approximately five fictional suppliers, five contracts, and three months of synthetic demand forecasts.
- Dated, attributable external market research.
- Retrieval of relevant fictional procurement documents.
- Bounded research with explicit uncertainty handling.
- Deterministic financial exposure scenarios with visible assumptions.
- One integrated risk assessment and mitigation report per request.
- Selected functional and failure tests, including missing contract prices and unavailable external APIs.
- Two reviewable example reports as planned prototype evidence.

### Should-have (v2)
- A second ingredient and broader procurement coverage.
- Improved evidence-quality evaluation and additional report review feedback.
- Pilot use with approved data and users, subject to access and security review.

### Nice-to-have (v3+)
- Continuous monitoring and alerts.
- ERP/S&OP integrations.
- Operational dashboards and wider deployment governance.

### Explicit exclusions
No real confidential procurement data, live ERP integration, autonomous purchasing, supplier approval, verified supplier capacity, negotiated quotes, production service-level guarantees, or unattended procurement commitments.

**MVP boundary:** Prioritize a reliable end-to-end sunflower oil assessment before expanding ingredients, integrations, or autonomous capabilities.

## 4. Risk Assessment

Probability and impact are **preliminary planning judgments**, not measured risk estimates.

| Risk | Probability | Impact | Proposed mitigation |
|---|---|---|---|
| Outdated, irrelevant, or contradictory external evidence | Medium | High | Preserve sources/dates; check relevance and comparability; perform bounded follow-up research; disclose unresolved conflicts |
| Missing or inconsistent contracts and forecasts | Medium | High | Validate required fields; use read-only queries; mark calculations unavailable rather than invent inputs |
| Commodity benchmark mistaken for contracted supplier price | Medium | High | Label benchmark data and assumptions separately; prohibit presentation of scenarios as quotes |
| Hallucinated supplier qualification or capacity | Medium | High | Label external candidates unverified; require human qualification and approval |
| External API failure, limits, or latency | Medium | Medium | Set request/iteration/time budgets; retry temporary failures; return partial or failed status transparently |
| LLM/API and integration costs exceed expectations | Medium | Medium | Cap tool calls and research rounds; track token/API costs during pilot; avoid optional components without demonstrated need |
| Sensitive data or credential exposure in later pilots | Medium | High | Use synthetic data for prototype; protect secrets; apply least privilege and review data access before real deployment |
| Reports are not trusted or useful to procurement managers | Medium | High | Review example reports with users; capture corrections; compare against current workflow and decision needs |
| Scope creep and orchestration complexity | High | Medium | Build sunflower-oil vertical slice first; defer MCP, extra ingredients, and production integrations |

**Operational ownership for a future deployment:** Procurement owns decision rules and approvals; a technical owner maintains integrations, logging, access, and incidents; source/data owners maintain contract and forecast quality. Named owners would be agreed before a real pilot.

## 5. Implementation Plan

Implementation will proceed in stages. Durations below are **preliminary estimates**, to be refined after confirming API access, data readiness, and the technical approach.

| Phase | Estimated duration | Activities | Exit milestone |
|---|---|---|---|
| 1. Setup and data preparation | 1–2 weeks | Confirm user requirements and report schema; prepare synthetic supplier, contract, forecast, and policy records; assess external-source suitability and access | Representative input and validated sample data are available |
| 2. Core agent development | 2–3 weeks | Implement bounded research and evidence review; connect structured/document retrieval; implement and test deterministic exposure calculations; assemble report | A sunflower-oil request produces a draft, traceable assessment |
| 3. Integration and testing | 1–2 weeks | Connect n8n input and delivery; validate field mappings and report schema; test conflicting evidence, missing prices, external failures, and stopping limits | End-to-end workflow meets agreed functional acceptance criteria |
| 4. Deployment preparation and monitoring design | 1–2 weeks | Define logs, error notifications, ownership, access controls, cost tracking, human review, and pilot readiness criteria | Controlled pilot proposal with documented limitations and responsibilities |

**Key dependencies:** Accessible and relevant external sources; representative internal data; credentials and service setup; agreed financial assumptions; defined report structure; procurement stakeholder availability.

**Resources and roles:** A solution builder familiar with Python, APIs, and orchestration; a procurement subject-matter reviewer; and, before any real-data pilot, IT/security and data owners. Tools include an LLM API, research APIs, Python, LangGraph, n8n, and PostgreSQL; vector retrieval remains conditional on demonstrated need.

**Budget considerations:** Model tokens, search/API usage, database and hosting resources, development effort, integration maintenance, and procurement review time. There is no defensible cost estimate yet; usage should be measured during implementation and used to develop a pilot budget.

**Milestones and decision gates:** First validate that the data and sources support the requested analysis. Next verify that the agent can produce a correct, reviewable report under normal and failure conditions. Only then consider a controlled pilot with approved real data. Production deployment would require separate security, reliability, governance, and operational acceptance.

## 6. Success Metrics

### Prototype acceptance criteria
- The sunflower-oil request follows the intended research-to-report path.
- Material external claims include identifiable sources and dates.
- Synthetic internal records are retrieved correctly.
- Financial scenario results match independently checked deterministic calculations.
- Missing essential inputs do not produce invented financial values.
- Unverified supplier candidates are labeled as such.
- Selected API-failure and missing-data cases yield visible, understandable outcomes.
- Two example reports are available for human review during prototype validation.

These are proposed checks, not passed tests.

### Future business validation
| Measure | Proposed target or method | Evidence required |
|---|---|---|
| Report usefulness | Target: 80% of reviewed reports rated useful | Procurement-user reviews with a defined rating question |
| First-pass research preparation time | Target: 30% reduction in controlled pilot | Measured manual baseline and comparable pilot tasks, including correction time |
| Operational response to qualifying alerts (future scope) | Target: 90% reviewed within an agreed service window | Agreed alert definition, monitoring records, and accountable owner |
| Trust and decision quality | No numerical target established | User feedback, documented corrections, and review of decisions supported |
| Runtime reliability and cost | Thresholds to be established after prototype measurement | Execution logs, failure categories, latency, and API usage |

**Interpretation:** A technically correct report does not by itself prove time savings, adoption, or ROI. The pilot must compare outcomes against the existing procurement process.

---

*Project assumptions:* Bakery Foods Inc. and the internal procurement records are fictional. All targets, estimates, and risk ratings are proposed and must be validated. External research sources are candidates, not verified integrations. This document is a solution plan and does not claim a completed implementation or measured business impact.
