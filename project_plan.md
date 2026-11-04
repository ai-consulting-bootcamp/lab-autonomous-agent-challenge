# LEGALFLOW — Autonomous Agent Project Plan

## 1. Use Case
**Problem:** Small and medium-sized law firms manually review, classify and route prospective-client inquiries. This introduces delays and inconsistent record keeping.

**Target users:** Lawyers, paralegals and intake administrators in firms with approximately 2–30 lawyers.

**Current manual process:** Staff read the incoming message, identify the practice area, note missing information, assess urgency and enter the matter into an intake tracker.

**Proposed agent:** LEGALFLOW analyzes an incoming inquiry and generates a structured intake record for human review. The initial demonstration uses a fictional employment-law inquiry. It does not give legal advice or determine whether a case should be accepted.

**Verification:** A reviewer can compare the incoming inquiry with the AI's structured output and the row appended to Google Sheets.

## 2. Technology Stack
| Component | Choice | Reason / trade-off |
|---|---|---|
| Input | n8n Manual Trigger + Edit Fields | Repeatable test; not a live client-facing intake channel |
| AI | OpenAI GPT-4o-mini | Affordable structured extraction; possible misclassification and API costs |
| Agent workflow | n8n AI Agent node | Simplifies model orchestration; no tool-driven agent actions in this first version |
| Output enforcement | Structured Output Parser | Six predictable fields; does not guarantee factual correctness |
| Storage | Google Sheets | Easy to inspect and demonstrate; not suitable for real client confidentiality without additional controls |
| RAG | Not used | No external legal research is needed for simple triage; limits legal analysis |
| LangGraph | Not used | Extra state-machine complexity would not improve this single-path demo |

## 3. MVP Scope
**Included:** One manually triggered fictional inquiry; four-category classification (Employment Law, Tenancy Law, Contract Law, Other); short summary; Low/Medium/High urgency; missing-information extraction; department suggestion; human-review status; append-to-sheet output.

**Excluded:** Real client data, legal advice, live intake channels, source-grounded legal research, automatic client replies, automatic assignment, deadline calculation, matter acceptance and production deployment.

**Success measures:** One traceable end-to-end run, six populated output columns, correct mapping to a persistent sheet, and consistent human-review status. Future target: correctly classify at least 9 of 10 fictional labeled test cases (not yet measured).

## 4. Risk Assessment
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Misclassification or overstated urgency | Medium | High | Human review; test labeled inquiries; never rely on model alone for deadlines |
| Incorrect or missing data in fields | Medium | Medium | Structured parser, field validation, manual checks |
| Confidential information exposure | Medium | High | Fictional data only in lab; production privacy and access review before any real use |
| Google Sheets failure / duplicate rows | Medium | Medium | Monitor execution errors; introduce unique inquiry IDs and duplicate checks in v2 |
| Model API downtime / rate limits | Low–Medium | Medium | Retry policy and error notification in future version |
| Scope creep or low adoption | Medium | Medium | Limit MVP to a single intake pathway; interview potential users |

**First daily failure mode to monitor:** Missing, duplicated or incorrectly mapped Google Sheets intake records despite an apparently successful AI classification.

## 5. Implementation Plan
| Phase | Tasks | Estimated effort | Exit criterion |
|---|---|---|---|
| 1. Setup | Define fictional test input and sheet schema | 0.5 day | Input and six columns ready |
| 2. Core agent | Configure prompt, OpenAI and structured parser | 0.5 day | Valid structured output |
| 3. Integration | Append row to sheet and verify values | 0.5 day | One correct row |
| 4. Proof and review | Export sanitized workflow, capture run evidence, review risks | 0.5 day | Complete lab_proof.md |
| Later production work | Webhook intake, stronger validations, access controls, audit trail, escalation logic | To be estimated | Security-reviewed pilot |

**Dependencies:** n8n instance, OpenAI API access, Google Sheets access. **Roles:** Student developer and tester; hypothetical supervising lawyer for production review. **Budget:** Existing lab infrastructure and usage-based API calls; actual cost needs measurement.

## 6. Success Metrics
1. One workflow execution completes through the Google Sheets append node.
2. Input payload, model output, destination record and execution reference are archived together.
3. All six expected fields match the destination columns.
4. No credentials or real personal data appear in the repository.
5. Future accuracy target of 90% on ten independently labeled fictional inquiries; not yet verified.

## Limitations
The implemented workflow is a manually triggered **AI-assisted automation**, not yet an autonomous unattended service. There is no scheduling, monitoring, external tool selection or live intake trigger. A production-grade autonomous agent would require these capabilities and a separate privacy/security assessment.
