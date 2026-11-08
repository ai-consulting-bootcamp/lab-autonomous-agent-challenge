# Autonomous Agent Project Plan

**Lab:** Architect the Bot Someone Will Actually Pay For

**Use case:** AI Customer Support Agent

**Industry:** E-commerce / Online Retail (illustrative scenario)

**Status:** Planning only — Part 2 prototype is optional

## 1. Use Case

### Problem statement

Online retailers receive repetitive customer questions about deliveries, returns, refunds and order policies. Support representatives spend time answering similar questions manually, which can increase response times, workload and inconsistency.

### Proposed solution

An AI Customer Support Agent will answer common customer questions using approved company information and escalate complex or unresolved enquiries to a human representative. Access to live order details is outside the initial scope unless an authorised integration is added later.

### Target users

- **Customers:** Get timely answers to routine questions.

- **Customer service representatives:** Focus on cases requiring investigation or judgement.

- **Customer support managers:** Review escalations and service performance.

### Current manual process

1. Customer submits an enquiry.

2. A support representative reads and categorises it.

3. The representative searches relevant company policies or, where authorised, order information.

4. The representative drafts and sends a response.

5. Complex or unresolved cases are escalated.

### Example scenarios

- **Routine:** “Can I return shoes if the size doesn't fit?” The agent consults the approved return policy and answers with its applicable conditions.

- **Escalation:** “My refund was rejected, but I think the decision was wrong.” The agent routes the request to a human rather than deciding the dispute.

### Verification criteria (proposed targets, not measured results)

| Metric | Proposed target | Verification method |
|---|---|---|
| Answer accuracy | At least 90% | Compare responses to an approved answer key |
| Response time | Under 10 seconds for routine queries | Measure elapsed time in controlled tests |
| Escalation accuracy | 100% of predefined complex test cases | Check expected versus actual routing |
| Evidence quality | Answers grounded in approved policies | Review source references and policy consistency |
| Customer satisfaction | 80% positive feedback in a future pilot | Collect post-interaction feedback |

## 2. Technology Selection Framework

### 2.1 Technology selection questions

| Question | Decision | Explanation |
|---|---|---|
| Does it need external knowledge? | **Yes — RAG** | The chatbot needs approved company FAQs, shipping information and return policies rather than relying on the model's general knowledge. |
| Does it need to interact with external systems? | **Yes — limited integrations** | The Streamlit interface sends requests to a FastAPI backend, which calls the external LLM API and retrieves approved company documents. Live order systems are excluded from the MVP. |
| Does it need multi-step reasoning? | **No advanced reasoning** | The MVP retrieves relevant policy information, generates an answer and checks whether human escalation is needed. A simple LangChain retrieval pipeline is sufficient; LangGraph is unnecessary initially. |
| Does it need to integrate with business systems? | **No for the MVP** | No CRM, payment, inventory or order-management integration is planned. A Streamlit interface and FastAPI backend are sufficient. |
| Does it need to be autonomous? | **On-demand automation** | It responds automatically when a customer sends a message, but does not run independently on a schedule. Basic error handling and logging are still needed. |

### 2.2 Proposed technology stack

The technologies below are proposed for future implementation; no chatbot has been built for this planning lab.

| Component | Proposed technology | Purpose |
|---|---|---|
| Chat interface | Streamlit | Create a simple browser-based chat interface using Python. |
| Backend API | Python and FastAPI | Receive requests from Streamlit and return chatbot responses. |
| Application logic | Python | Coordinate retrieval, response generation and escalation. |
| Core LLM | OpenAI API | Understand questions and draft natural-language answers based on retrieved information. |
| RAG document source | Approved company FAQs and policy documents | Provide trusted information on deliveries, returns and refunds. |
| Embeddings | OpenAI embedding model | Convert document chunks and questions into searchable vectors. |
| Vector database | Chroma | Store and retrieve relevant document chunks. |
| Chunking strategy | Split documents into short overlapping sections | Preserve useful context while keeping retrieval focused; exact chunk size will be tested during implementation. |
| Agent framework | LangChain | Connect document retrieval and answer generation in a simple pipeline. |
| Orchestration | Python, FastAPI and LangChain; no n8n initially | Coordinate the on-demand chatbot workflow without an additional automation platform. |
| Other integrations | OpenAI API and local/approved document store | Support answer generation and retrieval; no live customer records in the MVP. |
| Human escalation | Display contact instructions or flag the enquiry for review | Avoid unsupported answers to account-specific or complex cases. |

### 2.3 Technology justification, alternatives and trade-offs

- **OpenAI instead of Anthropic or Gemini:** Chosen for familiarity and accessible developer tooling. Trade-offs include API cost, dependency on an external provider and the need to protect customer data.

- **RAG instead of LLM knowledge alone:** Company policies can change, so answers should be grounded in approved documents. Trade-offs include document preparation, retrieval errors and the need to keep source material updated.

- **Chroma instead of Pinecone:** Suitable for a small, local prototype without a managed vector database. Trade-off: production hosting, scaling and persistence would require additional planning.

- **LangChain instead of LangGraph:** A simple retrieval-and-answer workflow does not need complex agent state transitions. Trade-off: more sophisticated multi-step workflows may be harder to manage later.

- **Python, FastAPI and LangChain instead of n8n:** Use FastAPI to expose the chatbot backend and LangChain to manage retrieval and response generation. Trade-off: maintaining a separate backend adds setup and testing work, but makes the API reusable.

- **Streamlit instead of a custom HTML/CSS/JavaScript interface:** Streamlit offers a Python-based chat interface suitable for a small prototype. Trade-off: less control over detailed website styling and integration into an existing commercial storefront. Streamlit is proposed; its use in class is not confirmed.

- **FastAPI backend instead of calling the model directly from Streamlit:** Separates the user interface from the chatbot service and reflects a technology covered in class. Trade-off: two components must be started, connected and tested.

### 2.4 Operational considerations

- If relevant company information is missing or ambiguous, the chatbot should avoid guessing and direct the customer to human support.

- Log errors and basic response outcomes without storing unnecessary personal information.

- Keep API credentials in backend environment variables; never expose them in Streamlit responses or commit them to Git.

- Test answer accuracy, source relevance, response time and escalation behaviour before deployment.

## 3. MVP Scope

### 3.1 Project Objective

The Minimum Viable Product (MVP) is a simple AI-powered website chatbot for an online retail business.

The chatbot will answer frequently asked customer questions using approved company FAQs and policies. When a question cannot be answered reliably, it will direct the customer to human support.

The goal is to reduce repetitive customer service work, improve response times, and provide consistent information.

### 3.2 Feature Brainstorming

Potential features for the chatbot include:

- Answering frequently asked customer questions

- Retrieving information from company FAQ and policy documents

- Providing responses through a website chat interface

- Referring unresolved questions to human support

- Tracking customer conversation history

- Checking order and delivery status

- Supporting multiple languages

- Collecting customer satisfaction feedback

- Integrating with CRM and ticketing systems

- Generating customer support performance reports

### 3.3 Must-Have Features (MVP / Version 1)

1. **Website Chat Interface**

   - Customers can type questions into a simple chat widget.

   - The chatbot displays responses on the website.

2. **AI-Powered Question Answering**

   - The chatbot uses an LLM to understand customer questions.

   - It generates clear, customer-friendly responses.

3. **Knowledge Retrieval (RAG)**

   - The chatbot retrieves information from approved company FAQs and return-policy documents.

   - Answers are based on retrieved information rather than unsupported assumptions.

4. **Basic Human Escalation**

   - If relevant information is unavailable, the chatbot directs the customer to a human support contact.

   - The chatbot does not make refund or order-management decisions.

5. **Basic Error Handling**

   - The chatbot displays a fallback message when the AI service or document retrieval fails.

### 3.4 Should-Have Features (Version 2)

- CRM or helpdesk integration for creating support tickets

- Basic conversation history

- Customer satisfaction feedback

- Additional document types

- Improved escalation routing

### 3.5 Nice-to-Have Features (Version 3+)

- Multilingual customer support

- Order and delivery tracking through e-commerce APIs

- Customer account integration

- Automated support analytics and reporting

- More advanced conversation memory

- Omnichannel support through email and messaging platforms

### 3.6 MVP Boundaries

**Included in the MVP:**

- A simple website chat interface

- English-language customer questions

- Answers based on approved FAQ and policy documents

- Retrieval-Augmented Generation (RAG)

- Basic fallback and human support referral

- Basic error handling

**Excluded from the MVP:**

- Live order tracking

- Payment processing

- Automatic refunds

- Customer account authentication

- CRM and ticketing integrations

- Multilingual support

- Advanced analytics

- Complex autonomous decision-making

### 3.7 Success Metrics

The following are proposed targets for future testing, not achieved results.

| Metric | Proposed Target | Verification Method |
|---|---|---|
| Answer accuracy | At least 90% | Compare answers against approved FAQs using 20 test questions |
| Response time | Under 10 seconds | Measure response time during testing |
| Escalation accuracy | 100% of predefined escalation cases | Test 5 unsupported or complex enquiries |
| Knowledge reliability | No unsupported policy claims in test responses | Review responses against source documents |
| Website functionality | 100% of 10 basic interaction tests pass | Test message submission and response display |

### 3.8 Example MVP User Journey

**Customer question:**

"Can I return a dress if the size does not fit?"

**Expected chatbot behaviour:**

1. Receive the question through the website chat interface.

2. Retrieve the relevant return-policy information.

3. Generate an answer based on the approved policy.

4. Display the answer to the customer.

**Escalation scenario:**

"My refund was rejected. Can you reverse the decision?"

**Expected chatbot behaviour:**

1. Recognise that the request requires individual account investigation.

2. Avoid making a refund decision.

3. Direct the customer to a human support representative.

### 3.9 MVP Summary

The first version will focus on one core customer journey: answering common customer questions accurately using approved company information.

Advanced integrations and features will be postponed until the basic chatbot has been tested and validated.

## 4. Risk Assessment and Mitigation

### 4.1 Overview

The Website Customer Support Chatbot will use AI and Retrieval-Augmented Generation (RAG) to answer customer enquiries based on approved company information.

Although the solution aims to improve customer support efficiency, potential technical, business, and data-related risks must be considered before implementation.

The following risk assessment identifies possible problems, estimates their probability and impact, and proposes mitigation strategies.

Risk ratings are preliminary planning estimates and will be reviewed during testing.

### 4.2 Technical Risks

| Risk | Probability | Impact | Mitigation Strategy |
|---|---|---|---|
| AI hallucinations or inaccurate answers | High | High | Use RAG with approved company documents, require supporting evidence, and escalate questions that cannot be answered reliably. |
| OpenAI API failures or rate limits | Medium | Medium | Implement timeouts, limited retries, error logging, and a fallback message directing customers to human support. |
| Slow chatbot responses | Medium | Medium | Limit retrieved document chunks, use an appropriate AI model, and monitor response times. |
| Chat interface and retrieval integration failures | Medium | High | Test communication between Streamlit, FastAPI, the LangChain retrieval pipeline and the AI service before deployment. |
| Incorrect document retrieval | Medium | High | Test retrieval with sample questions, review chunking settings, and check whether retrieved information is relevant. |

### 4.3 Business Risks

| Risk | Probability | Impact | Mitigation Strategy |
|---|---|---|---|
| Low customer adoption | Medium | Medium | Provide a simple chat interface, clear instructions, and an easy way to contact human support. |
| Unexpected API and hosting costs | Medium | Medium | Set usage limits, monitor API consumption, and estimate operating costs before deployment. |
| Customer dissatisfaction with AI responses | Medium | High | Test responses against approved policies, collect feedback in a future version, and provide human escalation. |
| Resistance from customer service employees | Medium | Medium | Involve support employees during testing and position the chatbot as an assistant rather than a replacement. |
| Scope creep | High | Medium | Prioritise MVP features and postpone advanced integrations, multilingual support, and order tracking. |

### 4.4 Data Risks

| Risk | Probability | Impact | Mitigation Strategy |
|---|---|---|---|
| Outdated or incorrect company policies | Medium | High | Use approved documents, assign responsibility for updates, and review knowledge sources regularly. |
| Exposure of customer personal information | Medium | High | Avoid collecting unnecessary personal data, protect API credentials, and apply appropriate access controls. |
| Missing information in the knowledge base | High | Medium | Test common questions, identify documentation gaps, and refer unsupported enquiries to human support. |
| Incorrect or incomplete document processing | Medium | Medium | Validate document extraction and test retrieval before making documents available to the chatbot. |
| Biased or inconsistent responses | Medium | Medium | Use consistent response guidelines and evaluate answers across a representative set of customer questions. |

### 4.5 Risk Prioritisation

The following risks should receive particular attention during MVP development:

**Priority 1: Inaccurate AI Responses**

The chatbot could provide incorrect information about returns, refunds, or delivery policies.

Mitigation:

- Retrieve information from approved company documents.

- Avoid generating answers without sufficient supporting information.

- Refer uncertain cases to human support.

**Priority 2: Customer Data Privacy**

Customers may enter personal or sensitive information into the chatbot.

Mitigation:

- Minimise the collection of personal information.

- Do not connect the MVP to customer accounts or payment systems.

- Protect credentials and avoid exposing sensitive data in logs.

- Review applicable data protection requirements before deployment.

**Priority 3: Missing or Outdated Knowledge**

The chatbot may be unable to answer questions because the knowledge base is incomplete or outdated.

Mitigation:

- Maintain approved and updated company documents.

- Test the chatbot against frequently asked questions.

- Provide a fallback response when reliable information is unavailable.

### 4.6 Operational Monitoring

If the chatbot is deployed, the following indicators should be monitored:

- Frequency of failed API requests

- Chatbot response times

- Number of unanswered customer questions

- Frequency of human support referrals

- Accuracy of answers during periodic quality checks

- API usage and operating costs

Monitoring will help identify recurring failures and opportunities for improvement.

### 4.7 Risk Assessment Summary

The most important risks for the Website Customer Support Chatbot are inaccurate AI responses, customer data privacy, and missing or outdated company information.

These risks can be reduced through approved knowledge sources, careful testing, limited data collection, fallback responses, and human escalation.

The MVP will prioritise reliable customer support over advanced automation features.

## 5. Implementation Plan

### 5.1 Project Overview

**Project Name:** AI-Powered Website Customer Support Chatbot

**Industry:** E-commerce / Online Retail

**Target Users:** Online shoppers, customer service representatives, and customer support managers.

**Project Objective:**

Design an AI-powered website chatbot that can answer frequently asked customer questions using approved company FAQs and policy documents.

The solution aims to reduce repetitive customer service tasks, improve response times, and provide consistent information about returns, deliveries, and general store policies.

Questions requiring individual investigation or unsupported decisions will be referred to human customer support.

### 5.2 Proposed Technology Stack

The following tools are proposed for future development, not already implemented. FastAPI was covered in class; Streamlit is a proposed Python-based interface.

| Component | Proposed Technology | Purpose |
|---|---|---|
| Chat interface | Streamlit | Browser-based chatbot interface built in Python |
| Backend API | Python / FastAPI | Receive chat requests, invoke chatbot logic and return responses |
| Application logic | Python | Handle retrieval, escalation and fallback behaviour |
| Core LLM | OpenAI API | Understand questions and generate answers |
| Agent Framework | LangChain | Coordinate retrieval and response generation |
| Knowledge Retrieval | RAG | Retrieve relevant company information |
| Vector Database | Chroma | Store and search document embeddings |
| Embedding Model | OpenAI embeddings | Convert document text into searchable vectors |
| Orchestration | FastAPI, Python and LangChain | Manage the request-response workflow |

**Technology Justification:**

This technology stack was selected because it supports a relatively simple, modular chatbot architecture.

LangChain is suitable for connecting the language model to company documents without introducing the additional complexity of LangGraph.

Chroma provides a straightforward option for developing a document retrieval system.

Streamlit will provide the customer-facing chat interface. It will send requests to a FastAPI backend, which will call the Python/LangChain retrieval workflow and return the response. The separate backend adds some complexity but allows the chatbot logic to be reused independently of the interface.

n8n and LangGraph are not required for the initial MVP because the solution does not involve complex business-system integrations or advanced multi-agent reasoning.

### 5.3 MVP Scope

**Included in Version 1:**

- Basic website chat interface

- English-language customer questions

- AI-generated responses based on approved company FAQs

- RAG-based knowledge retrieval

- Basic fallback messages

- Referral to human customer support

- Basic error handling

**Excluded from Version 1:**

- Live order tracking

- Automatic refund processing

- Payment transactions

- Customer account access

- CRM integration

- Multilingual support

- Advanced reporting and analytics

Future versions may introduce helpdesk integration, customer feedback, conversation history, multilingual support, and order-tracking APIs.

### 5.4 Implementation Phases

The following phases describe a proposed future implementation.

#### Phase 1: Setup and Data Preparation

**Estimated Duration:** 1–2 days

Activities:

1. Set up the Python development environment for Streamlit and FastAPI.

2. Install required libraries and dependencies.

3. Prepare sample company FAQ and return-policy documents.

4. Configure access to the selected AI model.

5. Prepare the Chroma vector database.

6. Split documents into chunks and generate embeddings.

**Deliverable:**

A prepared development environment and searchable company knowledge base.

#### Phase 2: Core Chatbot Development

**Estimated Duration:** 2–3 days

Activities:

1. Configure the OpenAI model and create a basic FastAPI endpoint.

2. Create a LangChain retrieval pipeline.

3. Connect the model to the knowledge base.

4. Develop prompts for answering customer questions.

5. Define fallback and human escalation behaviour.

6. Test the chatbot with sample customer enquiries.

**Deliverable:**

A basic Python/LangChain chatbot workflow exposed through a FastAPI endpoint, capable of answering questions using company documents.

#### Phase 3: Streamlit–FastAPI Integration and Testing

**Estimated Duration:** 2–3 days

Activities:

1. Develop a simple Streamlit chat interface.

2. Connect the Streamlit chat interface to the FastAPI endpoint, which invokes the Python/LangChain retrieval workflow.

3. Display customer questions and chatbot responses.

4. Test common customer enquiries.

5. Test unsupported questions and escalation scenarios.

6. Check response accuracy, latency, and error handling.

**Deliverable:**

A functioning website chatbot prototype with basic validation results.

#### Phase 4: Deployment and Monitoring

**Estimated Duration:** 1–2 days

Activities:

1. Select suitable hosting for both the Streamlit interface and FastAPI backend.

2. Configure environment variables and secure API credentials.

3. Deploy the chatbot for controlled testing.

4. Enable basic error logging and monitoring.

5. Review API usage and response times.

6. Document known limitations and future improvements.

**Deliverable:**

A deployed test version with basic operational monitoring.

### 5.5 Proposed Timeline and Milestones

| Phase | Estimated Duration | Milestone |
|---|---|---|
| Setup and Data Preparation | 1–2 days | Knowledge base prepared |
| Core Chatbot Development | 2–3 days | Python chatbot workflow responds to test questions |
| Website Integration and Testing | 2–3 days | Website chatbot tested |
| Deployment and Monitoring | 1–2 days | Test deployment completed |
| **Total** | **6–10 working days** | **MVP ready for evaluation** |

The timeline is an initial estimate for future implementation. It may change depending on technical challenges and available resources.

### 5.6 Project Dependencies

The project depends on:

- Access to approved company FAQ and policy documents

- Availability of the OpenAI API

- A Python development environment

- Required Python libraries

- A working document retrieval system

- A website or test page for the chatbot interface

- Suitable hosting if deployment is required

The MVP does not depend on live customer accounts, payment systems, or CRM access.

### 5.7 Resources Needed

**People and Roles:**

For a small MVP, one developer may perform several responsibilities.

| Role | Responsibility |
|---|---|
| AI Developer | Configure the LLM, RAG pipeline, and chatbot logic |
| Python / Streamlit / FastAPI Developer | Build the chat interface and backend API, and connect them to the retrieval workflow |
| Customer Support Representative | Review FAQs, responses, and escalation scenarios |
| Project Owner | Define requirements, scope, and success criteria |

**Tools and Services:**

- Visual Studio Code

- Python

- Streamlit

- FastAPI

- LangChain

- Chroma

- OpenAI API

- GitHub

- Sample company FAQ and policy documents

- Hosting service for future deployment

### 5.8 Budget Considerations

The project will use free or open-source development tools where possible.

Potential costs include:

- OpenAI API usage for text generation

- OpenAI embedding API usage

- Hosting and deployment

- Storage and operational monitoring

- Future maintenance and knowledge-base updates

API and hosting costs will depend on usage volume, selected models, and deployment requirements.

A detailed budget will be prepared before production deployment.

### 5.9 Success Metrics and Verification

The following targets will be used to evaluate the MVP during future testing.

| Metric | Proposed Target | Verification Method |
|---|---|---|
| Answer accuracy | At least 90% | Evaluate 20 predefined FAQ questions |
| Response time | Under 10 seconds | Measure response latency |
| Escalation accuracy | 100% of predefined complex cases | Test 5 escalation scenarios |
| Knowledge reliability | No unsupported policy claims | Compare responses with approved documents |
| Website functionality | 100% of 10 basic interaction tests | Test message submission and response display |

These are proposed targets, not achieved results.

### 5.10 Risk Management During Implementation

The most important risks identified in Step 4 are:

1. **Inaccurate AI responses:** Mitigate using approved documents, retrieval validation, and human escalation.

2. **Customer data privacy:** Minimise personal data collection and secure credentials.

3. **Outdated company information:** Maintain and regularly review the knowledge base.

4. **API failures:** Use timeouts, limited retries, and fallback messages.

5. **Scope creep:** Keep advanced integrations outside the initial MVP.

Risk levels and mitigation strategies will be reviewed after testing.

### 5.11 Project Completion Criteria

The future MVP will be considered ready for evaluation when:

- Customers can submit questions through the website interface.

- The chatbot retrieves relevant approved company information.

- Responses can be checked against the source documents.

- Unsupported questions are referred to human support.

- Basic API failures produce an appropriate fallback response.

- The defined test cases have been executed and documented.

### 5.12 Conclusion

The AI-Powered Website Customer Support Chatbot is designed to improve the handling of repetitive customer enquiries in online retail.

The proposed solution combines an AI language model, Retrieval-Augmented Generation, and a simple website interface.

By limiting the MVP to frequently asked questions and basic escalation, the project remains manageable while offering potential business value.

This document represents the planning phase only. Implementation, testing, and deployment are proposed future activities and have not yet been completed.
