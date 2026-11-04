# Autonomous Agent Project Plan

# [Schedule Trigger: daily] → [RSS Read: regulator feed] → [Remove duplicates: new items only]
   → [Edit Fields: normalize] → [OpenAI: summarise + rate → JSON] → [Edit Fields: parse]
   → [If: relevant?] ─ true  → [Notion/Airtable: create record, route = alert] → [Alert: Slack / email / Notion]
                     └ false → [Notion/Airtable: create record, route = archive]

## 1. Use Case

Research assistant

Problem: Compliance teams check regulators’ sites by hand.
Path: Schedule trigger (every morning) → fetch an RSS feed from a regulator such as the EDPB or AFM → LLM summarises each item and rates how relevant it is → Notion page.
Routing rule: Relevance at or above your threshold alerts the team.
Why pick it: It’s fully autonomous, so the “monitor it daily” question fits naturally.

Target Users: 

Client profile 

Mid-sized retail and SME bank in the Netherlands, about 1,500 employees, supervised by DNB and AFM. Processes large volumes of customer personal data: identity documents (KYC), transaction data, credit scoring, fraud and AML monitoring, and marketing via its app. Uses cloud providers and external vendors, some outside the EU. Main GDPR exposure: profiling and automated decisions in credit and fraud, retention of KYC data, international data transfers, data breaches, and data subject requests.

Current Process: Employee's check regulators sites by hand.

Verify:

Why an agent, not plain automation?


## 2. Technology Stack

### 2.1 Technology selection questions
- External knowledge needed? 
Yes, the model needs to know what regulators publish each morning. THough RAG is not necessary. Could become useful at a later stage
- Interacts with external systems? 
Yes, it reads regulators feed, and writes a record to Notion
- Multi-step reasoning? 
No, fixed pipeline. No loops e.g.. 
So LangGrah would add unneeded complexity
- Integrates with business systems? 
Yes, will write in compliance system, and give alerts.
- Autonomous (runs without human input)? 
Yes. It runs daily on a schedule with nobody starting it. That brings in the requirements the framework lists:
    - a Schedule Trigger
    - error handling (the error workflow, Retry On Fail)
    - duplicate handling
    - monitoring, through the Executions list and error alerts

p.s. The brief says the use case should need “agent capabilities, not just simple automation”. Your answer to question 3 admits it’s a pipeline. Your justification is that the core step is judgement: deciding whether an item matters to this specific client, which a keyword filter can’t do. 

### 2.2 Stack
- Core LLM: GPT-5.4, could have probably ran a 'weaker' model to save cost
- RAG components: None in MVP, each item fits in the prompt, possible for a v2
- Agent framework: n8n's HTTP Request to OpenAI with a structured JSON output, no LangChain/LangGraph. It runs well in n8n.
- Orchestration: n8n (self-hosted), Schedule Trigger, error workflow
- Tools/integrations: RSS Read (EDPB feed), OpenAI API, Notion database (Items), Notion page (Regulatory alerts)

### 2.3 Justification
Choice          Why                          Alternative considered          Trade-off
n8n             good way to build workflow   Python script / LangChain

GPT 5.4     ,   Works well                  Smaller model (for mvp)         Bigger model fr possible v2
JSON mode   

No RAG in MVP   Not necessary, fits prompt  Vector DB   q                   -


Fixed pipeline,  n8n pipeline suits the usecase LangGraph state machine     Latency & cost (tokens)
no LangGraph

Notion database works with the assignment       AirTable                    -

RSS feed        -                             Scraping the website          -


## 3. MVP Scope

Must-have (MVP)

Daily scheduled run	- It’s what makes the workflow autonomous
Read one regulator’s RSS feed	-  The single input
Skip items already processed    -	Without it, every run re-logs the whole feed
Short summary per item	-   Saves the reader opening every link
Relevance score (1–5) and a reason, for one client profile  -	The judgement step: the “agent” part
One routing rule (score ≥ 4 → alert, else archive)  -	The decision the lab asks for
One record per item in Notion or Airtable (title, link, date, summary, score, route)    -   The output a reviewer can inspect
Alert for relevant items (Slack, email or a Notion page)    -	The visible value for the team
Error notification (your Day 2 error workflow)  -	An autonomous run that fails silently is useless

Should have

Several regulators or feeds	-   Same path, more inputs
Topic tags (e.g. AML, privacy, reporting)	-   Makes filtering and reporting possible
Retry on feed and OpenAI failures	-   Lowers the noise from temporary errors
Feedback field (“useful / not useful”) on each record   -	Lets you measure and tune accuracy
Weekly digest email	-   Fewer interruptions than single alerts
Deadline or effective-date extraction	 -  High value, but extraction is error-prone

Nice to have

Multiple client profiles, routed to different owners	-   Turns the tool into a product for consultancies
RAG over the client’s internal policies (“which policy does this affect?”)	-   Needs a vector database and access to client documents
Full-document analysis (PDF guidelines, consultations)	-   Long inputs, higher cost
Multi-language feeds (e.g. Dutch and German regulators)	-   Prompt and quality testing per language
Dashboard of trends over time	-   Reporting rather than core value
Sites without RSS (scraping)	-   Brittle; breaks when the site changes


Out of scope, stated explicitly
Everything in v2 and v3 above, plus:

legal advice or interpretation
automatic actions beyond alerting
a chat interface

## 4. Risk Assessment

Risk	Probability	    Impact	    Mitigation

Feed changes format, moves or goes offline, so the run fetches nothing or fails
Medium	
High	
Error workflow alert; alert when a run returns 0 items several days in a row; Retry On Fail on RSS Read

Alert fatigue: too many alerts, so the team stops reading them	
Medium	
High	
Tune the threshold on test data; move to a daily digest in v2

Copyright of regulator texts when storing full content	
Low	
Low	
Store title, link and your own summary, not the full text

## 5. Implementation Plan

# 5.1. Setup and data preparation	Pick the regulator feed; check it works; write the client profile; judge 3–5 items by hand; create the Notion/Airtable table; check credentials		Feed URL works; hand-rated test set saved	Regulator has a working RSS feed
2. Core agent development	Manual Trigger → RSS Read → Limit → Edit Fields → OpenAI (summary + score as JSON) → parse → If rule		5 test items scored; ratings compared with your hand judgements	Phase 1 test set; OpenAI credential
3. Integration and testing	Write records; alert on the true branch; duplicate handling; run twice; connect the error workflow		One clean end-to-end run in Executions; no duplicates on a second run	Destination shared with the integration (authorization)
4. Deployment and monitoring	Add the Schedule Trigger; publish; check the first scheduled run; collect evidence; write lab_proof.md; sanitize; open the PR		Scheduled run succeeds; PR submitted

# 5.2 Timeline and milestones
Put your real dates here. For example:

Planning done: today
Prototype working: the next lab day
First scheduled run checked: the morning after publishing


# 5.3 Resources

Team: you, as builder and domain expert. In a real project you’d add a compliance officer to validate ratings and act on alerts, and an owner who keeps the client profile current.
Tools: n8n, OpenAI API (gpt-5.4-mini), Notion or Airtable (free plan), Slack or email for alerts, GitHub.
Budget: keep this as a formula rather than a guess:
Tokens per item ≈ prompt + client profile + item snippet + output, roughly 1,000 tokens. Check total_tokens in a real run.
Items per month ≈ items per day × 30. One regulator usually publishes a handful a day, but check the feed’s history.
Monthly cost ≈ tokens per item × items per month × the current model price (look it up on OpenAI’s pricing page).
Add n8n hosting (cloud plan or self-hosted). Notion and Airtable free plans are enough for the MVP.

## 6. Success Metrics