## 1. Use Case: Salon Assistant (Telegram AI agent)

**Problem statement:**
A small hair salon receives many customer messages every day: questions
about prices, opening hours and services, plus booking requests. Staff
answer them by hand between appointments, so replies are slow and
booking requests sometimes get lost.

**Target users:**
- Salon customers who message the salon on Telegram
- The receptionist / salon owner, who reviews booking requests
  and handles escalated messages

**Current process (manual):**
Staff read every message on the phone, look up prices or opening hours,
type replies one by one, and write bookings into a paper calendar or
notebook. Busy times mean late replies and missed requests.

**Verify (how we know it's working):**
- FAQ questions get a correct answer based on the salon's FAQ document
- Every booking request creates one row in the Airtable booking tracker
- Unclear messages and complaints are flagged for a human instead of
  being answered by the bot


## 2. Technology Stack

### Technology selection questions
| Question | Answer | Reason |
|---|---|---|
| Needs external knowledge? | **Yes → RAG** | Prices, opening hours and services are salon-specific; the LLM doesn't know them |
| Interacts with external systems? | **Yes → tools/integrations** | Receives messages from Telegram, writes bookings to Airtable |
| Needs multi-step reasoning? | **Partly** | The agent must decide: answer from FAQ, log a booking, or escalate. One decision per message, so an agent is enough; full LangGraph is not needed for the MVP |
| Integrates with business systems? | **Yes → n8n** | Telegram and Airtable have ready-made n8n nodes |
| Autonomous (runs without human input)? | **Yes** | It answers customers 24/7, so it needs error handling and monitoring |

### Selected stack
- **Core LLM:** OpenAI gpt-5.4-mini (cheap and fast, good enough for short FAQ answers)
- **RAG:** Pinecone vector store, OpenAI text-embedding-3-small (512 dimensions),
  Recursive Character Text Splitter (chunk size 1000, overlap 200)
- **Agent framework:** n8n AI Agent node (built on LangChain) with Simple Memory
- **Orchestration:** n8n
- **Tools/integrations:** Telegram (input/reply), Pinecone (FAQ search),
  Airtable (booking tracker)

### Justification
- I already built each part in n8n (RAG with Pinecone, AI agent with memory,
  Telegram → Airtable), so the risk is low and setup is fast.
- n8n makes the flow visible, so the salon owner can see what happens.

### Alternatives considered
- **Python with LangChain/LangGraph:** more control, but more code to write
  and maintain, and no ready-made Telegram/Airtable connectors.
- **Notion instead of Airtable:** possible, but Airtable is easier to sort
  and filter as a booking list.
- **Local vector store (e.g. Chroma) instead of Pinecone:** free, but
  harder to host together with n8n.

### Trade-offs
- n8n is fast to build but less flexible for complex logic than code.
- Pinecone and OpenAI are paid cloud services (small cost, data leaves the salon).
- gpt-5.4-mini is cheaper but may be less accurate than a bigger model.

## 3. MVP Scope

### All possible features (brainstorm)
- Answer FAQ questions (prices, opening hours, services) from a salon FAQ document
- Log booking requests in Airtable
- Escalate unclear messages and complaints to a human
- Remember the conversation (memory)
- Reply to the customer on Telegram
- Confirm or reject bookings automatically based on a real calendar
- Send appointment reminders
- Support German and English
- Accept voice messages (speech-to-text)
- Show available time slots
- Weekly report for the salon owner (most asked questions, number of bookings)
- Connect to WhatsApp and Instagram too

### Feature categories
| Must-have (MVP) | Should-have (v2) | Nice-to-have (v3+) |
|---|---|---|
| Answer FAQ questions with RAG | Check a real calendar and confirm bookings | Voice messages |
| Log booking requests in Airtable | Appointment reminders | WhatsApp / Instagram |
| Escalate unclear messages to a human | German + English | Weekly report for the owner |
| Basic conversation memory | Show available time slots | |
| Reply on Telegram | | |

### MVP boundaries
**Included:**
- One channel: Telegram
- One knowledge source: one salon FAQ PDF
- One language: English
- Booking *requests* only (staff confirm them manually)
- Basic memory (last 5 messages)

**Out of scope (v2+):**
- Automatic booking confirmation or calendar access
- Multiple languages
- Other channels (WhatsApp, Instagram)
- Payments
- Analytics and reports

### Success metrics
- At least 8 out of 10 test FAQ questions answered correctly from the FAQ
- 100% of booking requests create a row in Airtable
- 0 answers invented outside the FAQ (agent says "I don't know" or escalates instead)
- Reply time under 10 seconds
- Fewer booking requests lost compared to the manual process

## 4. Risk Assessment

### Technical risks
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **Hallucination:** the agent invents prices or opening hours that are not in the FAQ | Medium | High | System message: "answer ONLY from the FAQ, otherwise escalate"; test with 10 known questions; include the source in answers |
| **Wrong chunking:** a question and its answer end up in different chunks, so the search misses the answer | Medium | Medium | Use chunk overlap (200); test typical questions after every FAQ update |
| **Embedding mismatch:** storing and searching use different models or dimensions | Low | High | Use the same model (text-embedding-3-small, 512) everywhere; note it in the plan |
| **Integration failure:** Telegram, Pinecone or Airtable is down, or a token expires | Low | High | n8n error workflow that alerts the owner; retry on fail; check credentials monthly |
| **One bot = one workflow:** reusing the Telegram bot in a second workflow silently stops the first one | Low | High | One dedicated bot per workflow; document it |
| **API costs:** many messages cause high OpenAI costs | Low | Medium | Use gpt-5.4-mini; limit answer length; set a monthly spending limit in OpenAI |

### Business risks
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **User adoption:** customers prefer calling or don't trust the bot | Medium | Medium | Friendly greeting, clear "you can always reach a human" message, QR code in the salon |
| **Staff change management:** staff forget to check Airtable for new bookings | Medium | High | Daily check routine; v2: notification for each new booking |
| **Scope creep:** adding calendar booking, WhatsApp etc. too early | Medium | Medium | Stick to the MVP list; new ideas go to v2 |

### Data risks
| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **Outdated FAQ:** prices change but the FAQ PDF is not updated | High | High | Owner updates the FAQ when prices change; re-upload replaces old chunks (avoid duplicates) |
| **Privacy (GDPR):** names, usernames and chat IDs are personal data; Airtable stores data in the US | Medium | High | Store only what's needed; inform customers in the bot's welcome message; check GDPR with the salon |
| **Data quality:** photos, stickers or empty messages create broken rows | Medium | Low | If node: only continue when the message has text |
| **Duplicate FAQ data:** uploading the FAQ twice stores every chunk twice | Medium | Low | Clear the Pinecone namespace before re-uploading |

## 5. Implementation Plan

### Phases
| Phase | What happens | Time |
|---|---|---|
| **1. Setup & data preparation** | Write the salon FAQ (prices, hours, services); create Telegram bot, Airtable booking table, Pinecone index; save credentials in n8n | 1 day |
| **2. Core agent development** | Workflow to upload the FAQ into Pinecone; AI Agent with system message, memory, FAQ search tool and Airtable booking tool | 2 days |
| **3. Integration & testing** | Connect Telegram trigger and reply; test 10 FAQ questions, 5 booking requests, 3 unclear messages; fix wrong answers | 1–2 days |
| **4. Deployment & monitoring** | Publish the workflow; error workflow that alerts the owner; weekly check of executions and answers | 1 day + ongoing |

### Key milestones
1. FAQ stored in Pinecone and searchable
2. Agent answers FAQ questions correctly in the n8n chat
3. Booking requests from Telegram appear in Airtable
4. All test cases pass → MVP live

### Dependencies
- The salon owner must provide correct prices, hours and services for the FAQ
- Phase 2 needs Phase 1 done (index, credentials, FAQ)
- Accounts and API keys: OpenAI, Pinecone, Airtable, Telegram

### Resources needed
**Team & roles**
- Me: builder (workflows, prompts, testing)
- Salon owner: provides FAQ content, approves answers, reviews bookings
- Receptionist: checks Airtable daily, handles escalated messages

**Tools & services**
n8n, OpenAI API, Pinecone, Airtable, Telegram

**Budget considerations**
- OpenAI: pay per use; small model and short answers keep costs low
- Pinecone, Airtable, Telegram: free plans are enough for the MVP
- n8n: hosting or cloud plan cost
- Set a monthly spending limit in OpenAI

## 6. Success Metrics
(same as in section 3)
- At least 8 out of 10 test FAQ questions answered correctly
- 100% of booking requests create a row in Airtable
- 0 invented answers outside the FAQ
- Reply time under 10 seconds
- Staff report fewer lost booking requests after 1 month

# Autonomous Agent Project Plan
## 1. Use Case
## 2. Technology Stack
## 3. MVP Scope
## 4. Risk Assessment
## 5. Implementation Plan
## 6. Success Metrics