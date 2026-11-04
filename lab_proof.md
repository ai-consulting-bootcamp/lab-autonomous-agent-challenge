# 
After writing project_plan.md, i used the reviewer prompt to analyse my plan, this is the output, 3 risks:

1. Dedup runs before anything durable, so a failure loses items silently.
“Remove duplicates: new items only” marks an item as seen when it passes, not when it is safely stored. If OpenAI times out or Notion rejects the write, the next daily run treats that item as already seen and drops it. Nothing fails and nothing gets alerted. Two related problems:

Unstable key: what is the dedup key? Regulator feeds often have missing or reused guids, or they republish an item with a changed link or title. A link-based key then re-alerts, and a title-based key misses corrections.
Test runs: manual test runs can write to the same seen-history. Testing on today’s items may make tomorrow’s production run skip them.

2. A failed LLM parse falls quietly into “archive”.
If the OpenAI output arrives wrapped in ```json fences, has a missing key, or gives "relevant": "true" or "score": "8" as strings, your Edit Fields parse either errors or yields empty or false values. The If node then sends the item to the false branch and archives it as irrelevant. The worst case is a high-relevance item that ends up archived because the JSON was malformed. You need a third outcome, “unparseable”, that can never share the archive path. Also check how the If node compares types. A string compared against a boolean or number is a classic silent mismatch.

3. The alert-branch write and the alert are not atomic, and the destination schema is strict.

Route without delivery: the record gets route = alert before Notion or email fires. If the alert fails, the database claims someone was alerted when nobody was. Add a delivery status field, or write the route after the alert succeeds.
Strict Notion and Airtable fields:
Select options such as alert/archive and any category values must already exist, unless typecast is on in Airtable.
Dates must be ISO format.
Notion rich text has a per-block length limit, which long LLM summaries can exceed.
An empty title can fail the whole create.
Retries: a retry on create without an idempotency key, such as the source guid as a unique field, can produce duplicate records.
Two trace checks

1. One known item, end to end, run twice.
Pick one real feed item and note its guid. Follow it through the RSS output, the dedup pass, the raw OpenAI response, the parsed fields, the If branch taken, the record ID, and the Slack message timestamp. Then run the workflow again. The same item must be stopped at dedup with zero items downstream. This one check proves both the mapping and the dedup behaviour.

2. The failure and empty paths.
Use pinned data to push through a malformed LLM response, such as fenced JSON with one key missing. Confirm it lands in an error or “needs review” path and not in archive. Then run on a day with zero new items and confirm there is no error and no empty alert. On every run, reconcile the counts: items after dedup should equal alert + archive + errors. If they don’t, something is leaking.

One simplification

Use one “create record” node instead of two.
Set route with an expression before the branch, write the record once, then let the If node gate only the alert. You get one field mapping to maintain instead of two copies that drift apart, and schema errors surface in one place.




     Relevance: {{ $('Parse').item.json.relevance }}/5 · {{ $('Parse').item.json.topic }}
     Summary: {{ $('Parse').item.json.summary }}
     Why: {{ $('Parse').item.json.reason }}
     Link: {{ $('Parse').item.json.link }}