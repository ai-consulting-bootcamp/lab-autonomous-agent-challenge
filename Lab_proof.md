# Lab Proof: Architect the bot someone will actually pay for

**Use case:** RCSA Evidence & Challenge Agent (operational risk, Second Line review support)
**Stack:** LangGraph (Python) · OpenAI API (model set by `OPENAI_MODEL`) · local TF-IDF retriever · Wikipedia + Tavily Search APIs
**Code:** https://github.com/muratcomez1/AI-assisted-RCSA
**Plan:** see [`project_plan.md`](project_plan.md)

## 1. Critical path tested

```
INPUT:   CSV of process-risk pairs (owner's RCSA answers) for one process
DECIDE:  required fields = Pair ID, Process, Risk ID, Risk, Loss events (count), Loss amount (EUR),
                           KRI, Previous RCSA, Control, Applicable
         routing rule   = invalid input -> skip to finalize (failure report); valid -> full path
         destination    = outputs/reports/rcsa_challenge_<process>_<timestamp>.md + run log JSON
BUILD:   trigger (run_rcsa.py) -> validate -> rules -> retrieve -> external -> LLM challenge -> report -> finalize
VERIFY:  run of 2026-11-13 15:53, process "Payment Processing", status COMPLETED
```

## 2. Workflow configuration (LangGraph)

From `rcsa_agent/graph.py`:

```python
def build_graph():
    g = StateGraph(RCSAState)
    g.add_node("validate_input", nodes.validate_input)
    g.add_node("apply_rules", nodes.apply_rules)
    g.add_node("retrieve_evidence", nodes.retrieve_evidence)
    g.add_node("external_research", nodes.external_research)
    g.add_node("llm_challenge", nodes.llm_challenge)
    g.add_node("build_report", nodes.build_report)
    g.add_node("finalize", nodes.finalize)

    g.add_edge(START, "validate_input")
    g.add_conditional_edges("validate_input", nodes.route_after_validation,
                            {"continue": "apply_rules", "abort": "finalize"})
    g.add_edge("apply_rules", "retrieve_evidence")
    g.add_edge("retrieve_evidence", "external_research")
    g.add_edge("external_research", "llm_challenge")
    g.add_edge("llm_challenge", "build_report")
    g.add_edge("build_report", "finalize")
    g.add_edge("finalize", END)
    return g.compile()
```

Routing rule (`rcsa_agent/nodes.py`):

```python
def route_after_validation(state: dict) -> str:
    return "abort" if state.get("fatal_error") else "continue"
```

Trigger: `python run_rcsa.py` (defaults: `--process "Payment Processing"`, LLM and external tools on).

## 3. Input payload

**Graph input (trigger)**, built in `run_rcsa.py` for this run:

```json
{
  "data_path": "",
  "process": "Payment Processing",
  "out_dir": "outputs/reports",
  "use_llm": true,
  "use_external": true,
  "run_log": []
}
```

`data_path` is empty, so `find_default_csv()` in `rcsa_agent/data_loader.py` loads `data/rcsa_synthetic_data.csv`.

**Rows loaded for "Payment Processing"** (`data/rcsa_synthetic_data.csv`, synthetic data):

```csv
Pair ID,Process,Risk ID,Risk,Loss events (count),Loss amount (EUR),KRI,Previous RCSA,Control,LE flag,KRI flag,Key,Scenario ID,Applicable,Expected result,Anomaly
P08,Payment Processing,R1,Process execution error,2,5800,,N,None,Y,N,YNN|None,8,Yes,High - residual = inherent,
P09,Payment Processing,R2,Third-party failure,3,10800,,N,Not effective,Y,N,YNN|Not effective,9,Yes,High - action required,
P10,Payment Processing,R3,System outage,1,4300,,N,Effective,Y,N,YNN|Effective,10,Yes,"Conflict - effectiveness downgraded, residual floor applied",
P11,Payment Processing,R4,Data quality error,0,0,Data quality exceptions,Y,None,N,Y,NYY|None,11,Yes,High - residual = inherent,
P12,Payment Processing,R5,Unauthorized access or fraud,0,0,Overdue access reviews,Y,Not effective,N,Y,NYY|Not effective,12,Yes,High - action required,
P13,Payment Processing,R6,Regulatory non-compliance,0,0,Open regulatory findings,Y,Effective,N,Y,NYY|Effective,13,Yes,"Residual reduced, accepted",
P14,Payment Processing,R7,Key person dependency,2,7200,,Y,None,Y,N,YNY|None,14,Yes,High - residual = inherent,
```

## 4. Execution trace

Run log of the same run: `samples/rcsa_run_log_payment_processing_20261113_155312.json` (the `external` results block is shortened here, full file in the repo).

```json
{
  "status": "COMPLETED",
  "process": "Payment Processing",
  "run_log": [
    {"ts": "15:52:36", "node": "validate_input",    "status": "ok", "detail": "Loaded 7 process-risk pairs from data/rcsa_synthetic_data.csv"},
    {"ts": "15:52:36", "node": "apply_rules",       "status": "ok", "detail": "Rules applied to 7 pairs; 1 high review priority"},
    {"ts": "15:52:36", "node": "retrieve_evidence", "status": "ok", "detail": "Retrieved guidance for 7 pairs from 13 chunks"},
    {"ts": "15:52:38", "node": "external_research", "status": "ok", "detail": "Wikipedia Search API: ok, 5 items, 1 attempts"},
    {"ts": "15:52:38", "node": "external_research", "status": "ok", "detail": "Tavily Search API: ok, 5 items, 1 attempts"},
    {"ts": "15:53:12", "node": "llm_challenge",     "status": "ok", "detail": "7/7 challenges written by the LLM (gpt-6-luna); 0 deterministic fallback"},
    {"ts": "15:53:12", "node": "build_report",      "status": "ok", "detail": "Report assembled"},
    {"ts": "15:53:12", "node": "finalize",          "status": "ok", "detail": "Report saved to outputs/reports/rcsa_challenge_payment_processing_20261113_155312.md. Pending human review"}
  ],
  "external": {
    "wikipedia": {"tool": "Wikipedia Search API", "status": "ok", "attempts": 1, "items": ["... 5 items ..."]},
    "tavily":    {"tool": "Tavily Search API",    "status": "ok", "attempts": 1, "items": ["... 5 items ..."]}
  }
}
```

All 7 nodes ran in order, the conditional edge took `continue`, and no node fell back or failed.

## 5. Output record

Destination: `outputs/reports/rcsa_challenge_payment_processing_20261113_155312.md`, copied to `samples/` in the repo (`outputs/reports/` is git-ignored). Excerpt:

```markdown
# RCSA Challenge Report: Payment Processing

- Generated: 2026-11-13 15:53
- Run status: **COMPLETED**
- Data: synthetic demonstration data only
- Review: **human Second Line review required**. Approval: **Pending**

## 1. Summary

- Process-risk pairs analysed: 7 (7 marked applicable by the First Line)
- High review priority: P10
- Flags raised: ACTION_REQUIRED x5, CONTROL_CONFLICT x1, CONTROL_NOT_EFFECTIVE x2, LOSS_EVENTS_PRESENT x4, NO_CONTROL x3, NO_KRI_COVERAGE x4, RCSA_GAP x3

### P10: System outage (Payment Processing)

- LOSS_EVENTS_PRESENT: Historical loss events exist for this process-risk pair.
- RCSA_GAP: Risk is applicable but was not included in the previous RCSA.
- NO_KRI_COVERAGE: Information only: loss events exist but no KRI is assigned.
- CONTROL_CONFLICT: Control is described as Effective although loss events exist. Not automatic proof of control failure; needs human review.

**Challenge:** For Payment Processing, System outage is marked applicable and the control is described as effective, while one loss event of EUR 4,300 is recorded and the risk was absent from the previous RCSA (DATA:P10). The event does not by itself establish control failure; please explain its cause and timing and provide relevant control testing evidence (G-rcsa_challenge_guidance#2).

Evidence cited: DATA:P10, G-rcsa_challenge_guidance#2, G-rcsa_challenge_guidance#3 (challenge source: llm)

Reviewer decision: [ ] accept  [ ] request evidence  [ ] escalate
```

**Input → output check (what the reviewer can verify):**

| Pair | Input row (control, loss events) | `Expected result` in CSV | Rules result in report | Match |
|---|---|---|---|---|
| P08 | None, 2 LE | High - residual = inherent | High - residual = inherent | ✓ |
| P09 | Not effective, 3 LE | High - action required | High - action required | ✓ |
| P10 | Effective, 1 LE | Conflict - effectiveness downgraded, residual floor applied | same | ✓ |
| P11 | None, 0 LE | High - residual = inherent | High - residual = inherent | ✓ |
| P12 | Not effective, 0 LE | High - action required | High - action required | ✓ |
| P13 | Effective, 0 LE | Residual reduced, accepted | Residual reduced, accepted | ✓ |
| P14 | None, 2 LE | High - residual = inherent | High - residual = inherent | ✓ |

7/7 pairs match, and every LLM challenge cites the input pair ID (`DATA:Pxx`).

## 6. Mapping justification

| Input field | Used for | Why |
|---|---|---|
| `Applicable` + `Loss events (count)` | Challenge "not applicable" answers; `LOSS_EVENTS_PRESENT` | Core RCSA failure: owner denies a risk that already materialised |
| `Control` + `Loss events (count)` | `CONTROL_CONFLICT`, `NO_CONTROL`, `CONTROL_NOT_EFFECTIVE`, `ACTION_REQUIRED` | An "Effective" control with loss events needs evidence, not automatic acceptance |
| `Previous RCSA` | `RCSA_GAP` | Applicable risks missing from the last cycle point to coverage gaps |
| `KRI` | `NO_KRI_COVERAGE` (information only) | A missing KRI is a monitoring question, not proof of control weakness |
| `Pair ID` | Evidence ID `DATA:Pxx` in every challenge | The reviewer can trace each challenge back to the input row |

Flags and scenario results come from plain Python rules (`rcsa_agent/rules.py`). The LLM only drafts the challenge wording and questions, may cite only IDs it was given, and falls back to deterministic text if its JSON is invalid. The agent never gives numeric risk scores or approves controls; every report is "Pending human review".

## 7. Operational risk: first failure mode to monitor

**If this ran daily, the first thing I would monitor is the LLM step silently degrading to fallback.** `llm_challenge` falls back to deterministic text when the API fails or returns invalid JSON. The run still ends `COMPLETED`, so a daily job would look healthy while the reports lose their tailored challenges and owner questions. Monitor: the fallback count in the `llm_challenge` log line (`0 deterministic fallback` in this run). Alert if it is above 0 or if status is `COMPLETED_WITH_WARNINGS`.

Other risks to watch:
1. **Input schema drift:** if the business renames a column in the Google Sheet, `validate_input` aborts. This is handled (failure report saved), but a daily run needs an alert, not just a file.
2. **External tool outage or rate limits** (Wikipedia, Tavily): retries are built in (3 attempts, timeout, explicit status), but repeated `failed` status should be alerted on.
3. **Confidential data to external APIs:** with real data, process and risk names go to the LLM and search APIs. Keep synthetic data until there is a data processing agreement, and send only the fields needed.

## 8. AI usage (Prompt Discipline)

Main parts are done with AI. Actually ChatGPT could not handle it, so I shifted to Claude. Even though I say the main parts are done with AI, I can easily catch the mistakes or irrational things it has done. That's why I stopped using ChatGPT. But I am definitely not blindly copy-pasting whatever AI tells me. I ask for explanations and keep my notes and explanations on my Notion page. For example, for this Project 3 I have a 4-day diary about what was done, why and how, so that I can come back and read it in the future.
