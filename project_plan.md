# Autonomous Agent Project Plan

## 1. Use case

An inbound sales coordinator reads form submissions, decides which inquiries need a faster response, and copies contact details into a shared queue. The agent handles that first triage decision and leaves the actual response with the sales team. The prototype is verified by comparing the original inquiry and model decision with the saved Notion row.

## 2. Technology stack

| Selection question | Decision |
| --- | --- |
| External knowledge | The routing policy and message supply the necessary context. RAG, embeddings, chunking, and a vector database are outside the design. |
| External tools | OpenAI classifies the message. The Notion action creates the queue entry. |
| Multi-step reasoning | A single classification call plus a deterministic check covers the decision. A custom n8n Code node validates the result. |
| Business integration | n8n handles the data flow and gives the team execution logs. Notion provides a shared queue. |
| Autonomy | The prototype starts manually with one test inquiry. The pilot would start on form submission and report failed handoffs for human review. |

The prototype uses GPT-4o-mini. A keyword rule would avoid model cost but would need more examples to cover indirect descriptions of business needs. A standalone Python service would offer more control over deployment and testing while adding hosting and integration work. LangGraph would be worth revisiting if later versions needed branching research or follow-up state.

## 3. MVP scope

| Priority | Features |
| --- | --- |
| Must have | One English inquiry per run, two routing labels, a short reason, decision validation, and one Notion row for sales review. |
| Should have | Authenticated form intake, duplicate protection based on a submission ID, and alerts for incomplete handoffs. |
| Nice to have | Multilingual triage, CRM synchronization, analytics, and drafted follow-ups. |

The lab uses synthetic submissions and a test database. Customer messaging and production deployment are outside this prototype.

## 4. Risk assessment

| Category | Risk | Probability | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| Technical | Notion accepts a write with an omitted field. | Medium | High | Compare the returned properties with the prepared record. Alert on incomplete records in the pilot. |
| Technical | Model output fails parsing or contains an invalid route. | Medium | Medium | Validate the route and reason before writing. Keep failures visible in n8n. |
| Technical | A timeout or replay creates a duplicate. | Medium | Medium | Reconcile ambiguous writes against the queue. Use a stable submission ID before enabling automatic retries. |
| Business | Sales staff distrust labels or miss priority items. | Medium | High | Review decisions with the sales owner during the pilot and track overrides. |
| Business | New channels and auto-replies expand scope and cost. | Medium | Medium | Keep one source and one queue until the pilot meets its acceptance criteria. |
| Data | Messages contain sensitive information or misleading instructions. | Medium | High | Send only the message to the classifier, restrict access to credentials and logs, and keep sales review in the loop. |
| Data | Two synthetic examples hide weak performance on real inquiries. | High | Medium | Build a labeled pilot set with vague requests, indirect needs, and price questions with additional context. |

## 5. Implementation plan

| Phase | Estimate | Dependency and milestone |
| --- | --- | --- |
| Setup and data preparation | Half day | Test Notion database, two synthetic inquiries, and working n8n credentials. |
| Core development | Half day | Agreed routing policy. Classifier and decision validation produce a mapped record. |
| Integration and testing | One day | Notion property access. Both example routes are visible in the destination. |
| Pilot deployment and monitoring | Two days of setup plus a one-week review | Approved form access and labeled examples. Monitor incomplete writes, duplicates, and sales overrides. |

The builder owns the workflow and execution checks. The sales owner defines priority criteria and reviews disagreements. A workspace administrator manages access if needed. The prototype uses the course n8n account, one test database, and one model call per inquiry. The pilot budget depends on inquiry volume, token usage, hosting, and time spent on review.

## 6. Success metrics

The prototype passes when both example inquiries receive the expected route and all five mapped fields appear in Notion. Runs #2711 and #2712 meet that check. The initial missing Company value led to checking the written record as well as execution status.

Proposed pilot targets are at least 90% agreement with sales labels on 50 reviewed inquiries and at least 95% complete handoffs over one week. Median time from receipt to a triage decision would be compared with the current manual process. The two lab runs establish feasibility for these examples.
