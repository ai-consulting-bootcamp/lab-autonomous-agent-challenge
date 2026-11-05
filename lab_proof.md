# Autonomous Agent Project Plan

## 1. Use Case

### Selected use case
Customer Support Agent for a company that provides accounting, tax, and audit services.

### Problem statement
Clients request reports for a specific year and month, including the current month. Handling these requests creates extra work for employees, who need to search for files and coordinate with their team leader. Slow responses cause client dissatisfaction.

Some reports already exist in Google Drive. Other reports may not be ready yet, especially reports for the current month.

### Target users
The main users are clients who request their reports. Employees and their team leader handle approvals and requests that need human support.

### Current process
The employee receives a request by email or WhatsApp, identifies the client, and asks their team leader for permission to handle it.

After receiving approval by email, the employee checks the report type and requested period, searches for the document in Google Drive, and sends it to the client. Files are organized in folders by year, client, and month.

If the team leader does not approve the request, the employee asks the client to contact the team leader. If the report is not ready, the employee asks the team leader to review its priority.

### Proposed solution
When a client's email arrives, the system will record the request and ask the team leader for approval by email. The agent must wait for approval before searching for reports or asking the client for more information.

After approval, the agent will help identify the requested report and ask for missing information. The system must verify the client's identity and access permissions before searching the authorized client's Google Drive folder. Before delivery, it must confirm that the approval covers the selected report, period, and recipient.

Rejected requests, requests without permission, missing reports, and unclear cases will be sent to the responsible employee.

The MVP will not create reports or explain their content. Support for employees who prepare reports will be considered for v3 or later.

### Proposed verification criteria
- The report matches the authorized client, report type, month, and year.
- No report is sent without the team leader's approval.
- No documents belonging to other clients are sent.
- If information is missing, the agent asks for clarification before continuing.
- Requests without permission, missing reports, and unclear cases reach the responsible employee with the reason for human support.

These criteria are planned for future testing. This lab includes planning only. 

## 2. Technology Stack

### Technology selection
- External information: Yes. The system needs client permissions and report information from company systems.
- RAG: Not needed for this MVP. The system searches for files but does not answer questions about their content.
- External integrations: Yes. It needs email and Google Drive.
- Multi-step workflow: Yes. It receives and records the email, requests the team leader's approval, and waits for it. After approval, it understands the request, asks for missing information, checks the client's identity and permissions, and searches for the report. It then sends the approved report or sends the case to the responsible employee.
- Business system integration: Yes. n8n will coordinate these steps.
- Autonomy: Limited. The system can receive and record incoming emails automatically. It must receive the team leader's approval before searching for reports or asking the client for more information. Before delivery, it checks that the approval covers the report, period, and recipient. If the request changes, it asks for approval again.

### Selected technologies
| Component | Selection | Purpose |
|---|---|---|
| Core LLM | OpenAI | Understand requests written in natural language, extract the report type and period, and ask for missing information. |
| Orchestration | n8n | Connect the workflow steps and manage conditions, approvals, and errors. |
| Communication | Email | Receive requests, ask for clarification, request approval, and deliver reports. |
| File storage | Google Drive | Find existing reports in folders organized by year, client, and month. |
| Control records | Restricted request and approval register | Track each request, its status, and the approval linked to the client, report, period, and recipient. The storage tool still needs to be selected. |
| RAG components | None | A vector database, embeddings, and chunking are not needed for file searches. |
| Additional agent framework | None | n8n will coordinate the MVP. A separate LangChain or LangGraph application is not needed at this stage. |

### Reasons for these choices
Clients can write emails freely instead of using a fixed form. OpenAI will help understand different ways of asking for the same report. I have previous experience with OpenAI and n8n.

Google Drive is the company's current file storage system. The MVP will search for reports using the client, report type, year, and month.

Access permissions will be checked through system rules and company records. The model will not decide who has permission. Before delivery, the system must confirm that the team leader's approval matches the specific request and selected document.

### Alternatives considered and trade-offs
- A fixed form would make validation easier and reduce the need for AI. However, clients would lose the flexibility of writing requests in their own words.
- A custom Python application would provide more control, but it would require more development and maintenance.
- RAG would help answer questions about document content, but this function is outside the MVP.
- Human approval keeps the team leader's control, but response time still depends on their availability.
- Using an LLM adds API costs and a risk of incorrect extraction. Extracted fields must be validated before use.

### Operational controls and open decisions
The planned system needs error notifications, limited retries, request tracking, and duplicate detection to avoid repeated emails or deliveries.

Before implementation, the company must define how client identity and access permissions are verified. The sender's email address alone is not enough to prove identity.

The exact OpenAI model, email service, and storage tool for control records will be selected during setup. Report contents will not be sent to the LLM.

## 3. MVP Scope

### Must-have — MVP
- Receive client requests by email in Spanish and English.
- Record the request and ask the team leader for approval.
- Wait for approval before processing the request, searching for reports, or asking the client for more information.
- If approval is denied, record the decision and send the case to the responsible employee.
- After approval, identify the requested report type, year, and month.
- Reply in the same language as the client's email.
- Ask for clarification when required information is missing.
- Verify the client's identity and access permissions through system controls.
- Find existing PDF reports in Google Drive.
- Before delivery, check that the approval covers the report, period, and recipient. If these details change or are not covered, ask the team leader for approval again.
- Send the correct PDF to the authorized recipient.
- Send missing reports, unclear cases, and requests without permission to the responsible employee.
- Record the request status, approvals, delivery, or reason for human support.

### Should-have — v2
- Support additional languages.
- Add a dashboard to track requests and client satisfaction.
- Add WhatsApp as a communication channel.

### Nice-to-have — v3+
- Help employees prepare reports using approved procedures and templates, without sharing sensitive client data with the model.

### Out of scope for the MVP
- Creating reports or answering questions about their content.
- Giving accounting or tax advice.
- Sending Excel, Word, or other non-PDF files.
- Sending reports without the team leader's approval.
- WhatsApp, additional languages, and the dashboard.

### Planned success measures
- Correct identification of the report type and period in Spanish and English.
- Correct delivery of the requested PDF to the authorized client.
- No deliveries without approval or to unauthorized recipients.
- Correct routing of cases that need human support.
- Less employee time spent searching for and coordinating report requests.

Specific targets and test methods are defined in Section 6. These are planned measures, not observed results.

## 4. Risk Assessment

These probability and impact levels are initial estimates. They must be reviewed after testing.

| Category | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| Technical | The model identifies the wrong report type or period. | Medium | High | Validate the extracted fields and test requests in Spanish and English. After the leader's initial approval, ask the client to clarify unclear information. Do not guess missing values. |
| Business | The team leader takes too long to approve a request. | High | High | Send an email reminder after an agreed time. Keep the request blocked while approval is pending. Notify the responsible employee if the delay continues. |
| Data | The system selects another client's report or the wrong file. | Low | High | Limit searches to the authorized client's folder. Check the client ID, report type, year, and month using reliable records and file metadata. If information does not match or several files are found, stop delivery and request human review. |

### First failure to monitor
The first failure I would monitor is an incorrect file selection, because it could expose another client's information. I would review blocked mismatches and delivery records. If an incorrect delivery is detected, I would pause automatic delivery and notify the responsible team.

## 5. Implementation Plan

This is a future implementation plan. No development or testing has been completed for this lab.

### Phases and timeline
The estimated duration is 15 working days. Phases will run one after another, assuming the required people and access are available.

| Phase | Duration | Activities and milestone |
|---|---|---|
| 1. Setup and preparation | 1 day | Prepare folders, permissions, approval rules, and test examples. No tests are run in this phase. Milestone: preparation checklist completed. |
| 2. Core workflow development | 5 days | Configure request reception, registration, initial leader approval, request interpretation, and clarification. Validate settings with fictional data. Milestone: the main flow is ready for integration. |
| 3. Integration and testing | 4 days | Connect email and Google Drive. Test access controls, file searches, delivery, human support, and error handling. Milestone: critical tests pass and issues are recorded. |
| 4. Supervised pilot and monitoring | 5 days | Run a pilot with a small group, review results, and correct issues. Milestone: the team leader reviews the results and decides whether the system can continue. |

The workflow must wait for the leader's initial approval before searching for documents or asking the client for more information. Before delivery, it must check that approval still covers the request.

### Team and responsibilities
| Role | Responsibilities |
|---|---|
| AI Consultant | Define requirements, scope, risks, and success metrics. Coordinate with the company and evaluate pilot results. |
| AI Engineer | Configure n8n and OpenAI, connect email and Drive, implement controls and records, run technical tests, and fix errors. |
| Company employee | Explain the current process, prepare examples, and check that selected reports are correct. |
| Team leader | Define approval rules, approve requests, and decide whether to accept the pilot. |
| IT administrator | Provide accounts and access, configure permissions, and support security reviews. |

These roles do not require five full-time team members. One person may cover more than one role where appropriate.

### Dependencies
- Access to the company email service and Google Drive.
- An agreed method to verify client identity and access permissions.
- A selected storage tool for request and approval records.
- Clear report names and reliable file metadata.
- Approval rules, reminder times, and an assigned employee for cases that need human support.
- Availability of the team leader and employees for testing and the pilot.

### Resources and budget
Required resources include n8n, OpenAI API access, company email, Google Drive, restricted control records, and fictional test data.

The budget must include team working time, OpenAI API usage, n8n hosting or subscription, and any additional service costs. The amount still needs to be estimated based on request volume and the selected setup.

### Release condition
The pilot must not start until critical access and approval tests pass. If a serious issue appears during the pilot, automatic delivery will be paused and employees will use the manual process.

## 6. Success Metrics

These are proposed targets for future testing, not observed results.

| Metric | Target | Verification method |
|---|---|---|
| Correct identification of report type, year, and month | At least 16 out of 20 requests (80%). | Use 10 requests in Spanish and 10 in English. Compare all three extracted fields with the expected values prepared by an employee. Record results for each language. |
| Reduction in employee active working time | At least 30% compared with the manual process. | Measure employee working time for equivalent tasks before and during the pilot. Calculate: (manual time - pilot time) / manual time × 100. |
| Deliveries without permission or with another client's document | Zero cases. | Test unauthorized requests and incorrect file matches. Check delivery records, permissions, and approvals. |
| Approval control | All requests remain blocked until the leader approves them. | Test pending and rejected approvals. Confirm that no file search or client clarification happens before approval, and no report is sent without valid approval. |
| Routing to human support | All planned cases that need human support reach the responsible employee. | Test missing reports, rejected approvals, unclear requests, and requests without permission. Check that each case includes its status and reason for human support. |

### Interpretation and delivery
The 80% target applies only to request interpretation. It does not allow 20% incorrect deliveries.

Requests with unclear or inconsistent information must stop for clarification or human review. Before sending a report, the system must check access permissions and confirm that the file and approval match the request.

### Measurement limits
Employee active working time does not include waiting for the leader's approval. Approval waiting time and total response time will be recorded separately.

Passing a small test set does not guarantee that future requests will be error-free. Monitoring and human support remain necessary.
