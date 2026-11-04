# LEGALFLOW — Lab Proof

## Purpose
Demonstrate one input → AI transformation → Google Sheets output path for a legal intake assistant.

## Workflow configuration
See `legalflow_workflow_sanitized.json` (credential identifiers and spreadsheet link removed). To import it, reconnect Google Sheets and OpenAI credentials, supply your spreadsheet URL/tab, and ensure the sheet has the exact columns: `category`, `summary`, `urgency`, `missing_information`, `department`, `status`.

## Input payload (fictional)
```json
{
  "inquiry": "I received a termination letter yesterday. I worked for the company for five years. I want to know whether I can challenge my dismissal."
}
```

## Observed run
The n8n Executions screenshot shows run #2664 succeeded on 2026-11-04 at 22:19:02 (Europe/Berlin), duration 3.749 seconds. The screenshot is saved at `evidence/execution_2664.png`. The Google Sheets node returned one item; its JSON output was copied from n8n and is recorded below.

- Execution ID: **2664**
- Execution timestamp: **2026-11-04 22:19:02 Europe/Berlin**
- Execution status: **Succeeded**, **3.749 seconds**
- Execution screenshot: `evidence/execution_2664.png`
- Google Sheets node output (copied from n8n by the workflow operator):

```json
[
  {
    "category": "Employment Law",
    "summary": "Inquiring about the ability to challenge a termination after five years of employment.",
    "urgency": "Medium",
    "department": "HR or Legal Department",
    "status": "Human Review Required",
    "missing_information": "Details about the reason for termination and company policies."
  }
]
```

- Field completeness: **6 of 6 required keys populated**.
- Direct visual confirmation of the persisted sheet row: **not independently captured**. The successful Sheets node returned the record above; an optional screenshot of the destination row would strengthen the evidence.
- Quality note: urgency `Medium` may under-triage a time-sensitive employment termination; a production version should flag possible deadlines for qualified human review.

## Expected checks (not measured results)
1. The source contains one nonempty `inquiry` string.
2. The parser provides six fields in the output object.
3. A new Google Sheets row contains the same six field values.
4. The status is `Human Review Required`.
5. No unexpected duplicate row is created during a single execution.

## Mapping
`$json.output.category` → `category`; `$json.output.summary` → `summary`; `$json.output.urgency` → `urgency`; `$json.output.missing_information` → `missing_information`; `$json.output.department` → `department`; `$json.output.status` → `status`.

## Operational risk and mitigation
First daily concern: missing, duplicated or malformed rows. Check completed executions against new sheet rows; add an inquiry identifier and idempotency checks in a future version.

## Reflection
**Three risks:** model classification error; wrong field mapping; privacy leakage when using real inquiries.

**Two trace checks:** verify model output fields; compare values written to the destination row.

**One simplification:** no RAG or external agent tools in the MVP; use a single manually triggered input.

See `project_plan.md` for scope, stack, phases and mitigation choices. Fill the evidence placeholders with real records before submission; do not represent expected values as observations.
