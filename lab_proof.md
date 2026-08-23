# Lab Proof — Intellectus Impact Intake Triage Agent

## Bottom line

The critical path works: one synthetic social-organisation intake is validated, scored, routed and written as an inspectable consultant-review record. The committed success run exits `0`, creates priority score `85`, and routes the case to `senior_impact_consultant`. A second deliberately invalid event is blocked before scoring and routed to follow-up.

This is decision support, not automated client advice. `review_required` is always `true`.

## 1. Workflow export and configuration

The executable reference workflow is [`src/agent.py`](src/agent.py), configured by [`config/routing_rules.json`](config/routing_rules.json). An importable n8n manual-trigger version is provided at [`workflow/intellectus_intake_triage.n8n.json`](workflow/intellectus_intake_triage.n8n.json).

Critical path:

```text
INPUT: synthetic intake JSON
  → VALIDATE: required fields, allowed values and positive beneficiary count
  → TRANSFORM: readiness score, priority score and risk flags
  → ROUTE: follow-up, impact consultant or senior impact consultant
  → ACTION: write one auditable consultant-review record
```

The Python run below is the executed proof. The n8n file is an importable production-orchestration mapping; this submission does not claim a hosted n8n execution.

## 2. Input payload

Source: [`input/sample_payload.json`](input/sample_payload.json)

```json
{
  "event_id": "evt-berlin-youth-001",
  "organization_name": "BridgeForward Berlin",
  "challenge_statement": "The organisation needs to reduce the six-week delay between receiving youth-support requests and assigning each case to a qualified programme coordinator.",
  "beneficiary_count": 1800,
  "urgency": "high",
  "requested_outcome": "Prioritised diagnostic and a consultant-ready discovery brief",
  "data_sensitivity": "special_category",
  "submitted_at": "2026-08-23T16:00:00Z"
}
```

All names and facts in the fixture are synthetic.

## 3. Required-field and destination mapping

| Input | Transformation | Destination field |
| --- | --- | --- |
| `event_id` | Lowercase and replace non-alphanumeric runs with `_` | `intake_id` (idempotency key) |
| `urgency` | Versioned points: 10–40 | `priority_score` |
| `beneficiary_count` | Versioned reach band: 5–25 points | `priority_score` |
| `data_sensitivity` | 0, 10 or 20 points; creates handling flag | `priority_score`, `risk_flags` |
| Challenge and outcome length | Explicit completeness checks | `readiness_score`, `priority_score` |
| Score + sensitivity | Senior threshold or sensitivity rule | `route` |
| Required/allowed-value checks | Block invalid events | `status`, `missing_fields`, `validation_errors` |
| `submitted_at` | Preserved unchanged | `processed_at` |

## 4. Execution trace

Full trace: [`evidence/execution_trace.md`](evidence/execution_trace.md)

Executed command:

```bash
python3 src/agent.py \
  --input input/sample_payload.json \
  --output evidence/output_record.json
```

Observed stdout:

```json
{"event_id": "evt-berlin-youth-001", "status": "ready_for_consultant_review", "route": "senior_impact_consultant", "output": "evidence/output_record.json"}
```

Observed exit code: `0`

## 5. Output record

Destination artifact: [`evidence/output_record.json`](evidence/output_record.json)

```json
{
  "intake_id": "intake_evt_berlin_youth_001",
  "source_event_id": "evt-berlin-youth-001",
  "organization_name": "BridgeForward Berlin",
  "processed_at": "2026-08-23T16:00:00Z",
  "rules_version": "1.0.0",
  "review_required": true,
  "status": "ready_for_consultant_review",
  "http_status": 200,
  "route": "senior_impact_consultant",
  "priority_score": 85,
  "priority_band": "critical",
  "readiness_score": 100,
  "missing_fields": [],
  "validation_errors": [],
  "risk_flags": [
    "special_category_data_requires_authorised_handling",
    "high_beneficiary_reach",
    "time_sensitive_case"
  ],
  "summary": "BridgeForward Berlin submitted a high-urgency challenge affecting approximately 1800 beneficiaries. A consultant must verify the diagnosis before client use."
}
```

Output SHA-256: `4abbbe5dcc3a624b90af00606181f81791ad96e197d92a2b96f6bea5e53129ed`

## 6. Failure evidence

Fixture: [`input/invalid_payload.json`](input/invalid_payload.json)  
Artifact: [`evidence/invalid_output_record.json`](evidence/invalid_output_record.json)

The event omits `requested_outcome`, uses unsupported values for `urgency` and `data_sensitivity`, and supplies a non-positive beneficiary count. The agent returns:

- `status = needs_information`
- `http_status = 422`
- `route = intake_follow_up`
- `priority_score = null`
- one missing-field message and three explicit validation errors

This is the principal mapping guardrail: incomplete or changed upstream data cannot silently receive a business priority.

## 7. Verification

```bash
python3 -m unittest discover -s tests -v
python3 -m json.tool workflow/intellectus_intake_triage.n8n.json > /dev/null
python3 -m json.tool evidence/output_record.json > /dev/null
```

Observed test result: **4 tests passed**.

## 8. Operational risk and first monitor

The first daily failure mode to monitor is **input schema drift**. If the upstream form renames a field or introduces a new allowed value, the agent could send many records to follow-up. Monitor the daily validation-failure rate and unseen error reasons; alert above 10% or on any new reason.

The first operational control is a stable `intake_id` derived from the source event and organisation. A production destination must upsert on this key so retries do not create duplicate cases.

## 9. Scope and decision rationale

The complete use-case selection, technology framework, MVP prioritisation, risk assessment, phases, timeline, resources and metrics are in [`project_plan.md`](project_plan.md). The MVP deliberately excludes LLM and RAG calls because the critical decision is based on explicit business rules. This makes the evidence reproducible, keeps API cost at zero and reduces hallucination risk. n8n remains the target for production triggers and business-system integration.
