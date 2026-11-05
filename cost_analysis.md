## Cost analysis

I built this estimate from measured Python demo tokens and runtime, official price pages checked on 2026-11-05, and the explicit assumptions below. Monthly and annual totals are known-cost subtotals, not complete production budgets. The Cohere production rerank API rate is not available, evidence has no separate query-embedding or one-off KB embedding token usage, and n8n has no measured token trace. I show those values as not available and exclude them from totals.

### Assumptions (table)

| Item | Value and source |
|---|---|
| Measured LLM tokens per lead | 1431.00 input and 173.75 output, from four Python demos; includes the input-guard lead with zero tokens. |
| Measured Python runtime | 2.4249 seconds per lead, mean of four measured demo traces. metrics.json rounds this to 2.4 seconds. |
| Python LLM calls | 3 of 4 demo leads called the LLM, or 0.75 calls per demo lead. An accepted, unguarded lead invokes the chain once. |
| n8n LLM calls and tokens | not available because the evidence has a workflow export but no measured n8n execution or token trace. |
| Lead volumes | 100, 1,000, and 10,000 leads per month, as requested. |
| Projection horizon | 12 months, as requested. |
| Growth scenarios | Conservative: 100 flat. Expected: 300 starting leads, 10% monthly growth. High: 1,000 starting leads, 20% monthly growth. I round projected leads to the nearest whole lead. |
| Rerank calls | 1 per lead, as requested. This assumes every lead reaches retrieval, including guarded leads. |
| Airtable records | 1 record per lead, as requested; I assume one create-record API call per lead and no unrelated workspace calls. |
| Airtable editors | 3 editors, as requested. |
| Airtable starting state | I assume the base starts empty and has no other records. Free record limits can arrive earlier if existing records are present. |
| KB embedding size | 43 chunks for the requested one-off estimate. I treat this as an assumption; the project plan says the latest Pinecone read had 611 records. |
| One-off KB embedding cost | not available because the exact embedding token count for the assumed 43 chunks is not in evidence. |
| Query embedding tokens | not available because separate embedding token usage is not in evidence; embedding cost is excluded. |
| Cohere trial limit | The project plan states 1,000 API calls per month. I could not verify that monthly count in current Cohere official pages; Cohere confirms trial calls are free and rate-limited. |
| n8n Cloud executions | I assume one workflow execution per lead when modeling Cloud. The official Starter allowance is 2,500 per month and Pro is 10,000 per month. |
| Currency conversion | 1 EUR = 1.1224 USD, so I use 1 USD = 0.890948 EUR. ECB reference rate checked 2026-11-05. |
| Manual SDR time | 15.00 minutes per lead, an assumption because project_plan.md Section 1 describes manual steps but does not measure their duration. |
| SDR hourly cost | €40.00 per hour, an assumption using the example requested. |
| One-off build effort | 6.5 hours from project_plan.md Section 5. I value those hours at the assumed SDR rate, €40.00/hour, as a proxy rather than a measured engineering rate. |
| Production path | I model an always-on Render service, Pinecone Builder, n8n Cloud, and Airtable upgraded when its record limit is reached. The Python app is the modeled API path; n8n API usage is not measured. |

### API costs (per lead, per month table)

I price the Python LLM from measured average token counts, including the guarded demo with zero LLM tokens. Query embedding, one-off KB embedding, and production rerank are excluded because usage or price is not available.

| API part | Python app per lead | n8n agent per lead |
|---|---|---|
| GPT-5.4-mini input | $0.0011 | not available because n8n tokens are not measured |
| GPT-5.4-mini output | $0.0008 | not available because n8n tokens are not measured |
| Query embedding | not available because embedding tokens are not measured | not available because embedding tokens are not measured |
| Cohere trial rerank | $0.0000 while trial quota lasts | $0.0000 while trial quota lasts |
| Cohere production rerank | not available because the official per-search rate is not published | not available because the official per-search rate is not published |
| Known priced subtotal | $0.0019 | not available because n8n tokens are not measured |
| Full production API cost | not available because embedding usage and Cohere rate are missing | not available because n8n usage, embedding usage, and Cohere rate are missing |

| Leads/month | Python known LLM subtotal | Query embedding | Cohere production rerank | Full Python production API | n8n API |
|---|---|---|---|---|---|
| 100 | $0.19 | not available, token usage missing | not available, per-search price missing | not available | not available, n8n usage missing |
| 1,000 | $1.86 | not available, token usage missing | not available, per-search price missing | not available | not available, n8n usage missing |
| 10,000 | $18.55 | not available, token usage missing | not available, per-search price missing | not available | not available, n8n usage missing |

### Infrastructure costs (demo vs production table, limits)

The production option starts with Render always-on hosting, Pinecone Builder, n8n Cloud, and paid Airtable Team for three editors. At 10,000 leads per month, the first month uses n8n Pro and Airtable Team; Airtable Business is needed in month 5 if 10,000 new records are added each month. Cohere production is an API charge and is not included in the infrastructure figures. The 12-month projection starts from free Airtable while it fits and changes plans when a free limit is reached.

| Leads/month | Demo plans | Production, month 1 | Free limit that forces an upgrade |
|---|---|---|---|
| 100 | €0.00 initially; Free records reach 1,000 in month 10 | €108.20 known infrastructure | Airtable Free records at month 10 if base starts empty; no monthly Airtable or Cohere cap. Render sleeps after 15 idle minutes. |
| 1,000 | free quotas hit in month 1; not sustainable after 1,000 leads | €108.20 known infrastructure | Airtable Free record cap and 1,000 API calls reached in month 1; Cohere trial 1,000-call project-plan limit reached. Render sleeps after 15 idle minutes. n8n Cloud Starter remains under its 2,500-execution tier. |
| 10,000 | free quotas exceeded in month 1; not viable at this volume | €138.20 known infrastructure | Airtable Free record/API limits and Cohere trial limit exceeded in month 1; Airtable Team 50,000-record cap reached in month 5. Render sleeps after 15 idle minutes. n8n Cloud Starter 2,500-execution tier exceeded; Pro is 10,000 executions. |

I assume one Airtable API call per lead. At 100 leads per month, an empty Free base reaches 1,000 records in month 10. At 1,000 leads per month it reaches the Free record and monthly API-call limits in month 1. At 10,000 leads per month it exceeds both in month 1. The project plan states a 1,000 monthly Cohere trial-call figure; I could not independently confirm that number in current official Cohere pages. Render Free sleeps after 15 idle minutes, so I budget the $7 always-on web service from month 1 for production. Pinecone Starter usage cannot be projected because evidence lacks measured storage and read units per query.

### Technology comparison (table + recommendation)

I price both LLMs against the same measured tokens. OpenAI currently marks GPT-4o-mini as deprecated, so I show its lower price as a comparison only.

| Choice | Cost per 1,000 leads or plan cost | Trade-off from my evidence |
|---|---|---|
| LLM: gpt-5.4-mini, current | $1.86 | Current. Measured tokens; structured output works. Keep while the four demo outputs pass. |
| LLM: gpt-4o-mini | $0.32 | Much cheaper on the same measured token count, but the official model page marks it deprecated. |
| Reranker off | $0.00 incremental | Plain search put the 2025 archive first for the Plus query. |
| Reranker on, current | not available for production | Reranked search also put the 2025 archive first; current evidence shows no fix for this query. |
| n8n self-hosted | license $0; server not available | Free Community Edition. Hosting, power, backups, and maintenance are not priced. |
| n8n Cloud Starter | €20.00 per 1,000 leads at 1,000/month | 2,500 executions per month; price shown billed annually. |
| Python app on Render | €6.24 per 1,000 leads at 1,000/month | Always-on web service starts at $7/month; simple chain and one measured LLM call for accepted leads. |
| Airtable Free | $0.00 while within limits | 1,000 records per base and 1,000 API calls per workspace per month. |
| Airtable Team, three editors | $72.00 monthly, €64.15 per 1,000 leads at 1,000/month | Typed fields and easy review; 50,000 records per base. Business is needed after that cap. |
| Google Sheets | $0.00 standard API usage | Lower cost, but the lead schema, validation, and workflow logic need more code. 10 million cells per spreadsheet. |

At 10,000 leads per month, I would keep gpt-5.4-mini and run the Python app on Render, move the lead log to Airtable Business by month 5 if volume stays there, and pause Cohere reranking until a retrieval check proves it fixes the archive result and its production price is available.

### 12-month budget projection (table with year totals per scenario)

I use the Python app as the modeled API path. These totals include GPT-5.4-mini token cost, Render, Pinecone, n8n Cloud, and Airtable plan changes at documented limits. They exclude query embedding and production Cohere reranking, so they are lower bounds. I exclude one-off build effort from run costs and show it in the value check.

| Scenario | Month | Leads | API known subtotal | Infrastructure known cost | Total known subtotal | Cohere status |
|---|---|---|---|---|---|---|
| Conservative | 1 | 100 | €0.17 | €44.06 | €44.22 | trial quota not hit |
| Conservative | 2 | 100 | €0.17 | €44.06 | €44.22 | trial quota not hit |
| Conservative | 3 | 100 | €0.17 | €44.06 | €44.22 | trial quota not hit |
| Conservative | 4 | 100 | €0.17 | €44.06 | €44.22 | trial quota not hit |
| Conservative | 5 | 100 | €0.17 | €44.06 | €44.22 | trial quota not hit |
| Conservative | 6 | 100 | €0.17 | €44.06 | €44.22 | trial quota not hit |
| Conservative | 7 | 100 | €0.17 | €44.06 | €44.22 | trial quota not hit |
| Conservative | 8 | 100 | €0.17 | €44.06 | €44.22 | trial quota not hit |
| Conservative | 9 | 100 | €0.17 | €44.06 | €44.22 | trial quota not hit |
| Conservative | 10 | 100 | €0.17 | €108.20 | €108.37 | trial quota not hit |
| Conservative | 11 | 100 | €0.17 | €108.20 | €108.37 | trial quota not hit |
| Conservative | 12 | 100 | €0.17 | €108.20 | €108.37 | trial quota not hit |
| Expected | 1 | 300 | €0.50 | €44.06 | €44.55 | trial quota not hit |
| Expected | 2 | 330 | €0.55 | €44.06 | €44.60 | trial quota not hit |
| Expected | 3 | 363 | €0.60 | €44.06 | €44.66 | trial quota not hit |
| Expected | 4 | 399 | €0.66 | €108.20 | €108.86 | trial quota not hit |
| Expected | 5 | 439 | €0.73 | €108.20 | €108.93 | trial quota not hit |
| Expected | 6 | 483 | €0.80 | €108.20 | €109.00 | trial quota not hit |
| Expected | 7 | 531 | €0.88 | €108.20 | €109.08 | trial quota not hit |
| Expected | 8 | 585 | €0.97 | €108.20 | €109.17 | trial quota not hit |
| Expected | 9 | 643 | €1.06 | €108.20 | €109.27 | trial quota not hit |
| Expected | 10 | 707 | €1.17 | €108.20 | €109.37 | trial quota not hit |
| Expected | 11 | 778 | €1.29 | €108.20 | €109.49 | trial quota not hit |
| Expected | 12 | 856 | €1.41 | €108.20 | €109.62 | trial quota not hit |
| High | 1 | 1,000 | €1.65 | €108.20 | €109.86 | production price not available |
| High | 2 | 1,200 | €1.98 | €108.20 | €110.19 | production price not available |
| High | 3 | 1,440 | €2.38 | €108.20 | €110.58 | production price not available |
| High | 4 | 1,728 | €2.86 | €108.20 | €111.06 | production price not available |
| High | 5 | 2,074 | €3.43 | €108.20 | €111.63 | production price not available |
| High | 6 | 2,488 | €4.11 | €108.20 | €112.32 | production price not available |
| High | 7 | 2,986 | €4.94 | €138.20 | €143.14 | production price not available |
| High | 8 | 3,583 | €5.92 | €138.20 | €144.13 | production price not available |
| High | 9 | 4,300 | €7.11 | €138.20 | €145.31 | production price not available |
| High | 10 | 5,160 | €8.53 | €138.20 | €146.73 | production price not available |
| High | 11 | 6,192 | €10.23 | €138.20 | €148.44 | production price not available |
| High | 12 | 7,430 | €12.28 | €138.20 | €150.48 | production price not available |
| Conservative year total | 12 months | 1,200 | €1.98 | €721.11 | €723.10 | known subtotal only |
| Expected year total | 12 months | 6,414 | €10.60 | €1,106.00 | €1,116.60 | known subtotal only |
| High year total | 12 months | 39,581 | €65.42 | €1,478.45 | €1,543.87 | known subtotal only |

The chart above shows the known monthly subtotal for each scenario. These are not complete production budgets until Cohere's production rate, query-embedding usage, and one-off KB embedding tokens are measured or confirmed.

### Value and payback (table)

I assume manual qualification takes 15.00 minutes per lead because Section 1 lists the manual steps but gives no timing. I subtract the 2.4249-second measured Python runtime. I value SDR time at €40.00 per hour and value the plan's 6.5-hour build estimate at the same hourly rate. Payback uses month 1 volume and known monthly costs only, so it is optimistic while API prices are missing.

| Scenario | Month 1 leads | Time value saved | Known monthly cost | Value less known cost | One-off build proxy | Payback at month 1 run rate |
|---|---|---|---|---|---|---|
| Conservative | 100 | €997.31 | €44.22 | €953.08 | €260.00 | 0.27 months |
| Expected | 300 | €2,991.92 | €44.55 | €2,947.37 | €260.00 | 0.09 months |
| High | 1,000 | €9,973.06 | €109.86 | €9,863.20 | €260.00 | 0.03 months |

### Sources (price, URL, date checked)

| Price or source | Value or finding | Official source URL | Date checked |
|---|---|---|---|
| GPT-5.4-mini input and output rates | $0.75 input and $4.50 output per 1M tokens | [https://developers.openai.com/api/docs/models/gpt-5.4-mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini) | 2026-11-05 |
| GPT-4o-mini rates and deprecation status | $0.15 input and $0.60 output per 1M tokens | [https://developers.openai.com/api/docs/models/gpt-4o-mini](https://developers.openai.com/api/docs/models/gpt-4o-mini) | 2026-11-05 |
| text-embedding-3-small rate | $0.02 per 1M input tokens | [https://developers.openai.com/api/docs/models/text-embedding-3-small](https://developers.openai.com/api/docs/models/text-embedding-3-small) | 2026-11-05 |
| Cohere production API and trial status | production per-search price not available; official page says production is pay-as-you-go | [https://cohere.com/pricing](https://cohere.com/pricing) | 2026-11-05 |
| Pinecone Starter and Builder | $0 Starter; $20 Builder per month | [https://www.pinecone.io/pricing/](https://www.pinecone.io/pricing/) | 2026-11-05 |
| Airtable Free and Team pricing | $0 Free; $24/editor/month monthly or $20 annual | [https://airtable.com/pricing](https://airtable.com/pricing) | 2026-11-05 |
| Airtable record/API limits and Business price | Free 1,000 records and calls; Team 50,000 records and 100,000 calls; Business $54/editor/month monthly | [https://support.airtable.com/articles/2277136852-airtable-plans-overview](https://support.airtable.com/articles/2277136852-airtable-plans-overview) | 2026-11-05 |
| Render Free and always-on service | $0 Free; $7/month smallest always-on web service | [https://render.com/pricing](https://render.com/pricing) | 2026-11-05 |
| n8n Cloud Starter and Pro | €20/month Starter and €50/month Pro, billed annually | [https://n8n.io/pricing/](https://n8n.io/pricing/) | 2026-11-05 |
| n8n self-hosted Community Edition | software license is free; server price not available | [https://support.n8n.io/article/can-i-use-your-license-for-my-use-case](https://support.n8n.io/article/can-i-use-your-license-for-my-use-case) | 2026-11-05 |
| Google Sheets API | standard API use has no additional charge; 300 writes/minute/project and 60/user/minute | [https://developers.google.com/workspace/sheets/api/limits](https://developers.google.com/workspace/sheets/api/limits) | 2026-11-05 |
| Google Sheets account and file limit | any Google Account can create Sheets; 10 million cells per spreadsheet | [https://developers.google.com/workspace/sheets/api/limits](https://developers.google.com/workspace/sheets/api/limits) | 2026-11-05 |
| ECB exchange rate | 1 EUR = $1.1224 on 2026-11-05 | [https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.es.html](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.es.html) | 2026-11-05 |
