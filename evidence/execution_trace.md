# Execution Trace

Execution date: 2026-08-23  
Environment: Python 3, standard library only  
Workflow configuration: `config/routing_rules.json` version `1.0.0`

## Successful run

Command:

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

Trace checks:

| Stage | Evidence observed |
| --- | --- |
| Input | Event `evt-berlin-youth-001`; input SHA-256 `f54586d19273368ca2403dc416e30f40d0ad8f16941d79eb501017dc4cb80269` |
| Configuration | Rules version `1.0.0`; rules SHA-256 `28c7e2a9934060b53c220a75e77675e9bd5d870d16eaf0cac1bfa48e0aafcdd6` |
| Validation | No missing fields or validation errors |
| Transformation | Priority `85`; readiness `100`; band `critical` |
| Routing | `senior_impact_consultant` because the input declares `special_category` data |
| Action/output | `evidence/output_record.json`; output SHA-256 `4abbbe5dcc3a624b90af00606181f81791ad96e197d92a2b96f6bea5e53129ed` |

## Controlled failure run

Command:

```bash
python3 src/agent.py \
  --input input/invalid_payload.json \
  --output evidence/invalid_output_record.json
```

Observed stdout:

```json
{"event_id": "evt-incomplete-002", "status": "needs_information", "route": "intake_follow_up", "output": "evidence/invalid_output_record.json"}
```

Observed exit code: `2` (intentional validation failure)

The output records one missing field, three validation errors, no priority score, and route `intake_follow_up`. Failure-output SHA-256: `a88ea0433cc63b2115b3608fc23ee43973b0d53ff136770cbd2c203bcaa922e6`.

## Automated verification

Command:

```bash
python3 -m unittest discover -s tests -v
```

Observed result:

```text
Ran 4 tests in 0.001s

OK
```

The four tests cover fixture validity, the successful route and expected scores, blocking an invalid event, and stable idempotency for replayed events.
