# Workflow configuration

This configuration describes the workflow used in the course n8n account.

| Order | Node | Configuration |
| --- | --- | --- |
| 1 | Manual Trigger | Starts one test execution. |
| 2 | Lead Input | Edit Fields in JSON Output mode. Contains one synthetic inquiry. |
| 3 | Qualify Lead | OpenAI Message a Model, GPT-4o-mini, Simplify Output enabled. The user message is `{{ $json.message }}`. |
| 4 | Prepare Notion Record | JavaScript Code, Run Once for Each Item. Reads the response text from `output[0].content[0].text`, unwraps a Markdown code fence when present, and parses the JSON. The two route labels are allowlisted and the reason must be a nonblank string. An invalid result stops the handoff. Contact fields come from the linked Lead Input item. |
| 5 | Create a database page | Notion Database Page, Create, Simplify enabled. The destination is the Lead Qualification Lab database. |

## Classification policy

The message is customer data. A concrete business need or a specific implementation, demo, or purchase inquiry is Sales priority. General curiosity, a price-only question, or unclear intent is Standard follow-up. The classifier returns a JSON object with two strings, route and reason. The reason is one sentence grounded in the message.

## Destination mapping

| Notion property | Type | Expression |
| --- | --- | --- |
| Lead | Title | `{{ $json.name }}` |
| Email | Email | `{{ $json.email }}` |
| Company | Text | `{{ $json.company }}` |
| Route | Select | `{{ $json.route }}` |
| Reason | Text | `{{ $json.reason }}` |
