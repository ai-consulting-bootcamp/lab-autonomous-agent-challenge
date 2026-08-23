# Autonomous Agent Project Plan

## 1. Use Case

### Selected use case

**Intellectus Impact Intake Triage Agent** — a narrow agent that turns one social-organisation intake event into an inspectable, prioritised record and routes it to the appropriate consultant queue.

### Problem statement

Social-impact consultancies often receive inconsistent discovery forms. A consultant must manually check completeness, estimate urgency and reach, identify sensitive-data handling needs, and decide who should review the case. This delays the first useful response and makes prioritisation inconsistent.

### Target users

- Primary: impact consultants and programme managers at Intellectus.
- Secondary: authorised intake coordinators at client social organisations.
- Data subjects affected indirectly: employees, volunteers, donors and beneficiaries described by the organisation.

### Current manual process

1. An organisation submits a challenge description.
2. A coordinator checks the form for missing information.
3. A consultant assesses urgency, beneficiary reach and data sensitivity.
4. The coordinator creates a case record and assigns it.
5. A consultant reviews the diagnosis before anything is sent to the client.

### Verification criteria

Given the committed sample payload, the workflow must create exactly one destination record with:

- `status = ready_for_consultant_review`
- `priority_score = 85`
- `priority_band = critical`
- `route = senior_impact_consultant`
- `readiness_score = 100`
- `review_required = true`

An incomplete or invalid payload must not be scored and must route to `intake_follow_up` with HTTP-equivalent status `422`.

## 2. Technology Stack

### Selection framework

| Question | Answer | Consequence |
| --- | --- | --- |
| External knowledge required? | No, not for the critical path | No RAG in MVP |
| External systems required? | Yes, later intake and case-management systems | n8n is the target orchestrator |
| Multi-step reasoning required? | Yes, but rules are explicit | A small state-like pipeline is sufficient; LangGraph would be excessive |
| Business-system integration required? | Yes in production | n8n after validation |
| Autonomous execution required? | Yes | Event trigger, validation, audit record and monitoring are required |

### Selected technologies

- **Core decision engine:** standard-library Python 3, with versioned JSON rules.
- **Core LLM:** none in the critical path. The triage decision must be reproducible and auditable.
- **RAG:** none for MVP; no external knowledge is needed to validate or route an intake.
- **Agent framework:** custom deterministic pipeline (`validate → score → route → record`).
- **Orchestration:** n8n manual-trigger workflow for the prototype; webhook and destination integration are production steps.
- **Tools/integrations:** JSON input now; case-management database or CRM later.

### Justification and trade-offs

Python makes the proof executable without credentials, while n8n matches Intellectus's integration-oriented business stack. Deterministic rules are safer than an LLM for routing cases that may involve vulnerable people or special-category data: the same input produces the same score, every rule is inspectable, and testing is cheap.

Alternatives considered:

- **LangChain agent:** rejected for MVP because no tool selection or open-ended language reasoning is necessary.
- **LangGraph:** useful if later versions add research, approval and remediation loops; excessive for one critical path.
- **LLM classification:** could draft a plain-language summary in v2, but must not control priority or access routing.
- **Pure n8n Code node:** included as an importable configuration, but the Python reference implementation is easier to test automatically and proves behaviour without a hosted instance.

## 3. MVP Scope

### Feature inventory and prioritisation

| Must-have (MVP) | Should-have (v2) | Nice-to-have (v3+) |
| --- | --- | --- |
| Required-field validation | Webhook trigger | CRM/database upsert |
| Allowed-value and type checks | Authentication | Controlled LLM summary drafting |
| Transparent priority score | Retry/error notification | Knowledge-base research |
| Readiness score | Persistent duplicate detection | Multilingual intake |
| Consultant queue routing | Dashboard and SLA alerts | Outcome analytics |
| Risk flags | Human override capture | Adaptive scoring proposals |
| Human-review requirement | Schema-version alert | Multi-agent workflow |
| Stable idempotency key | | |

### Included

- One JSON intake payload.
- One versioned transformation and routing rule set.
- One consultant-ready output record.
- One success path and one controlled failure path.
- Unit tests and an importable n8n workflow.
- Audit fields: source event, rules version, processing timestamp and stable intake ID.

### Excluded

- Automatic client-facing advice.
- Collection or storage of real personal data.
- External research, RAG or generative AI.
- Live CRM write, authentication, scheduling and deployment.
- Removal of consultant review.

### Success metrics

- 100% of incomplete or invalid test inputs are blocked before scoring.
- 100% deterministic replay: identical events create the same `intake_id` and route.
- At least 95% of valid production intakes create a review record without manual re-entry.
- Median intake-to-queue time below 30 seconds after deployment.
- 0 cases sent to clients without authorised consultant review.

## 4. Risk Assessment

| Category | Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| Technical | Input schema changes silently break mappings | Medium | High | Version schema; reject invalid fields; alert on validation-failure rate |
| Technical | Repeated delivery creates duplicate cases | Medium | Medium | Stable `intake_id`; destination must upsert on that key |
| Technical | n8n or destination is unavailable | Medium | Medium | Queue retries, cap attempts, notify operator, preserve event ID |
| Technical | Scoring rules drift between Python and n8n | Medium | High | Treat JSON rules/Python as reference; add contract test before deployment |
| Business | Consultants distrust automated priority | Medium | Medium | Expose the score components; allow documented human override |
| Business | Scope expands into automatic consulting advice | Medium | High | Keep client-facing output explicitly out of scope; require change approval |
| Data | Sensitive personal information enters free text | High | High | Data-minimisation instructions; access control; retention limit; authorised review |
| Data | Rules disadvantage small organisations | Medium | Medium | Keep beneficiary reach as only one component; audit outcomes by organisation size |
| Data | Real data appears in test evidence | Low | High | Use synthetic organisations and payloads only; scan repository for secrets |
| Cost | Unnecessary LLM/API calls increase cost | Low | Medium | No LLM on MVP critical path; add only with measured benefit and spend limits |

### First daily failure mode to monitor

**Schema drift**, measured through the proportion and reason distribution of `needs_information` records. A sudden increase is the earliest sign that a form field, allowed value or upstream mapping changed. Alert when more than 10% of a daily batch fails validation or when any previously unseen validation error appears.

## 5. Implementation Plan

| Phase | Duration | Work | Milestone | Dependency |
| --- | ---: | --- | --- | --- |
| 1. Setup and data preparation | 0.5 day | Define schema, synthetic fixtures and rules | Input contract approved | Consultant owner |
| 2. Core agent development | 1 day | Implement validation, scoring, routing and output | Reference runner passes tests | Approved rule weights |
| 3. Integration and testing | 1 day | Import n8n workflow; connect webhook and test destination | One staging trace and record | n8n/CRM access |
| 4. Deployment and monitoring | 1 day | Add credentials, retry policy, alerts and runbook | Controlled staging release | Security and data-owner review |

### Resources and roles

- **Impact consultant/product owner:** approves fields, thresholds and override policy.
- **Automation developer:** maintains Python contract and n8n mapping.
- **Data protection/security reviewer:** approves access, retention and special-category-data controls.
- **Operations owner:** responds to validation and delivery alerts.

### Tools, services and budget

- Development: Python and GitHub, no incremental licence cost.
- Orchestration: existing n8n environment; no new service assumed for MVP.
- Model/API budget: €0 for MVP because no LLM call is required.
- Production budget depends on hosting, monitoring and destination-system licences; estimate only after the staging integration identifies actual event volume.

## 6. Success Metrics and Decision Gate

The prototype can advance to staging only when all automated tests pass, a reviewer reproduces the committed success record, the invalid fixture is blocked, the n8n mapping matches the reference output, and the data/security owners approve the retention and access model. Production use remains conditional on authentication, persistent idempotency, retry/error notification, monitoring and documented human override.

