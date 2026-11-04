Lab proof: Regulatory Update Monitor

An autonomous n8n workflow that reads the EDPB publications feed every morning, has an LLM summarise each new item and rate its relevance (1–5) for a mid-sized Dutch bank, logs every item in a Notion database, and creates an alert page for items rated 4 or higher.

Inspect first: the execution trace (section 2), then the output record (section 4) and the matching row in the Notion screenshot. The full project plan is in project_plan.md.

Proof piece	File
Workflow export (sanitized)	workflow/regulatory_monitor.json
Execution trace	evidence/execution_trace.png
Input payload	samples/input_item.json
Output record	samples/output_record.json, evidence/notion_items.png
Alert	evidence/alert.png
Duplicate test	evidence/dedupe_run1.png, evidence/dedupe_run2.png
1. Workflow export

File: workflow/regulatory_monitor.json. Credentials, Notion database/page IDs and instanceId removed.

Schedule Trigger (daily 07:30) ─┐
Trigger manually (testing) ─────┴─► RSS Read → Limit → Remove Duplicates → Normalize
   → Rate with OpenAI → Parse → Create a database page (Notion: Items)
   → If (route = alert) ─ true  → Create a page (Notion: Regulatory alerts)
                        └ false → (end: item already archived in Items)
Node	What it does
Schedule Trigger	Starts the run every day at 07:30 (production)
Trigger manually	Same path, for testing
RSS Read	Fetches https://www.edpb.europa.eu/feed/publications_en; one n8n item per publication
Limit	Caps items per run (<<FILL: your value>>) to control cost
Remove Duplicates	Remove items processed in previous executions, keyed on link; only new items continue
Normalize (Edit Fields)	Keeps title, link, published, snippet under stable names
Rate with OpenAI (HTTP Request)	gpt-5.4-mini, JSON mode; returns summary, relevance (1–5), topic, reason
Parse (Edit Fields)	Parses the JSON, adds route (alert if relevance ≥ 4, else archive) and processed_at
Create a database page	Writes every item as one row in the Notion database Items
If	route equals alert
Create a page	Alert page under Regulatory alerts with relevance, summary, reason, link

Settings: Error Workflow = Error alerts (creates a Notion page with workflow name, failed node, error message and a link to the run).

2. Execution trace

Execution trace

Execution ID: 2653
Date/time: 4 nov 20:05:16
Trigger: Manual
Items per node: RSS Read 10 → Limit 4 → Remove Duplicates 4 → Notion 4 → If true 4 / false 0
Tokens: <<FILL: total_tokens per item from the OpenAI output>>
3. Input payload

One item from the RSS Read output (full file: samples/input_item.json):

json
EDPB
/samples/input_item.json

4. Output record

json
output_record.json


Notion Items table

5. Mapping table
Source	Destination (Notion Items)	Transformation	Why
RSS title	Title	none	Readable name of the publication
RSS link	Link	none	Source of truth for the reader; also the dedupe key
RSS isoDate	Published	renamed to published; ISO 8601 date	Notion Date property needs ISO format (pubDate is RFC 822)
RSS contentSnippet (fallback content)	— (sent to OpenAI only)	renamed to snippet; empty string if missing	Input for the rating; not stored, to avoid copying source text
OpenAI summary	Summary	JSON.parse of the model's response	Lets the team triage without opening every link
OpenAI relevance	Relevance	JSON.parse; Number	Drives the routing rule
OpenAI topic	Topic	JSON.parse	Sorting and filtering
OpenAI reason	Reason	JSON.parse	Makes the score explainable, builds trust
derived from relevance	Route	relevance >= 4 ? 'alert' : 'archive'	One place where the route is decided
$now	Processed at	ISO timestamp	Audit trail: when the item was handled
6. Routing rule

Relevance ≥ 4 → alert, otherwise → archive. Every item is logged in Items; only alert items also create a page in Regulatory alerts.

The scale comes from the client profile in the system prompt: 5 = act now (final guidelines, opinions or decisions on profiling, AML/KYC data, international transfers, breach notification, financial-sector processing); 4 = review this month (drafts on those topics, enforcement against financial firms); 3 = good to know; 1–2 = not relevant. The prompt says "if unsure, choose the higher score" to reduce missed relevant items.

How the test items were routed:

Item	Relevance	Route	My own judgement	Match?
<<FILL>>				
<<FILL>>				
<<FILL>>				
7. Operational control

Duplicate detection (Remove Duplicates on link, across executions), proven by the run-twice test in section 8. Supported by an error workflow that creates an alert page when any node fails.

8. Trace checks
Run twice (idempotency). Run 1: <<FILL>> items written. Run 2: Remove Duplicates outputs 0 items, no new rows. Screenshots: evidence/dedupe_run1.png, evidence/dedupe_run2.png.
Malformed response. <<FILL: what you tested, e.g. forcing an invalid model or breaking the JSON, and what happened: error workflow page created / item routed>>.
9. First failure mode to monitor if run daily

<<FILL: your choice and reasoning. Candidates from the review:>>

Feed silently returns nothing (moved or changed URL): no error fires, the team assumes there was no news. Detect: alert when a run returns 0 items several days in a row.
Failed or partial LLM parse lands in archive: a missing relevance key makes relevance >= 4 false, so a relevant item is quietly archived. Detect: validate the parsed fields and route anything missing to alert or to the error workflow.
Dedupe runs before durable storage: if the Notion write fails after Remove Duplicates has marked the link as seen, the item is lost. Detect: error workflow alert on the Notion node, then clear that link from the dedupe history and re-run.
10. How I used AI

<<FILL: in your own words. E.g. used Claude and the portal's Workflow reviewer prompt for planning review, debugging (Notion property-key errors, Remove Duplicates mode, node references) and critique. What the reviewer found (three risks, two trace checks, one simplification) and what you changed as a result, e.g. one create-record node instead of two.>>