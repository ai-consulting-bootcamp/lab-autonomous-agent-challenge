# Lead Qualification Lab

The workflow turns one inbound inquiry into one Notion queue entry. It assigns a priority from the inquiry text and records the reason alongside the original contact fields.

- [Project plan](project_plan.md)
- [Workflow configuration](workflow_configuration.md)
- [Sofia input](evidence/sofia.json)
- [Execution #2711](evidence/execution-2711.png)
- [Notion output JSON as displayed in n8n](evidence/sofia-output.png)
- [Resulting Notion queue](evidence/notion-queue.png)

## Primary execution

On November 5, 2026, manual execution #2711 succeeded in 3.537 seconds. The trigger, input, classifier, record preparation, and Notion action each passed one item. The Notion action returned one created page in 708 ms.

| Notion field | Observed value |
| --- | --- |
| Lead | Sofia |
| Email | sofia@example.com |
| Company | Green Dental Clinic |
| Route | Sales priority |
| Reason | The customer has a concrete business need related to stopping phone bookings and is inquiring about a specific implementation of the software. |

The reason identifies the appointment-booking problem that triggered priority. The record preparation step reads the name, email, and company from the input and adds the validated model decision.

## Second case

[Tom's input](evidence/tom.json) produced a record for Bakery Miller with the route Standard follow-up. The model described the inquiry as a general price-only question without a specific need or intent. [Execution #2712](evidence/execution-2712.png) succeeded in 5.243 seconds.

## What the runs showed

Execution #2710 reported success even though Notion returned an empty Company field. The value was already present at the action's input. Correcting the property mapping restored the field in #2711 and #2712. The first daily check would look for accepted inquiries with a missing or incomplete Notion record, including records from executions marked successful. Each run uses Create, so replaying an inquiry can create a duplicate.
