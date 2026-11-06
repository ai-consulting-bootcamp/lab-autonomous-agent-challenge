# n8n assembly guide (not an export)

The repository was inspected on 6 November 2026. No n8n executable, Docker
runtime, n8n export, or configured LLM credential was available, so this file
is an assembly guide rather than an importable workflow. A JSON export is
deliberately not supplied: it would be unvalidated against the target n8n
version and could contain invented node parameters or credential IDs.

## Verified local path

The deterministic path is implemented and tested in
[`scripts/restaurant_discovery.py`](../scripts/restaurant_discovery.py). It
uses only the fictional read-only catalog in
[`fixtures/restaurants.demo.json`](../fixtures/restaurants.demo.json). Run it
from the repository root with:

```powershell
python scripts/restaurant_discovery.py --input fixtures/input.demo.json --trace
```

The command prints an observable structured output and a sanitized local trace.
It is a local fallback, not an n8n execution and not an autonomous LLM agent.

## Manual n8n workflow to assemble once n8n is available

Use the node names available in the installed n8n version and keep the stages
visible for review:

1. **Manual Trigger** — primary trigger for a repeatable demo run.
2. **Input payload** — add the two fields from `fixtures/input.demo.json`:
   `session_id` and `message`. Do not add names, phone numbers, or precise
   personal location data.
3. **Normalize & Validate Input** — reject a non-object payload, a missing or
   non-string `message`, and an empty/whitespace-only message. Return a
   structured error and do not continue to catalog lookup.
4. **Extract Search Preferences** — use the documented rule-based schema:
   `intent`, `city`, `cuisine`, `budget_max_eur`, `party_size`, `date`, and
   `time`. Unknown values remain `null` or `unknown`; do not describe this as
   LLM extraction.
5. **Enough Information for Discovery?** — require a city. If it is missing,
   return one targeted city question and set `search_performed` to `false`.
6. **Read Synthetic Catalog** — load the fictional fixture as a read-only
   source. Do not add live HTTP lookups, SQL writes, availability, or booking
   actions.
7. **Filter & Rank Matches** — apply city, requested cuisine, and known budget
   as hard constraints. If there are no exact matches, put any relaxed results
   in a separately labeled alternatives field; never silently present them as
   exact matches.
8. **Format Grounded Response** — include only restaurant IDs returned from
   the catalog, their explicit tri-state `booking_channel`, and
   `availability_checked: false`.
9. **Observable Output** — inspect the execution result in n8n and record the
   real execution ID, timestamp, node names, and output. Only then may the
   n8n-specific evidence section in `lab_proof.md` be changed from NOT RUN.

## n8n validation still required

After installing or connecting a permitted n8n environment, validate the
manual workflow against that exact version, export it from n8n, and run T01
plus the edge cases in the implementation brief. The optional AI-agent path
also requires a user-provided credential configured in n8n; no credential is
present in this repository and none is requested or embedded here.
