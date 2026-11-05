# Autonomous Agent Project Plan

## 1. Use Case
A job-application assistant that helps me and others to find suitable job postings, and maximize the chance of beeing invited for inteview trough tailoring the cv and application letter to the job posting. also gives help for the interview and on how to think about your dream job / finding the right job.

## 2. Technology Stack

no RAG needed. A knowledge base should be enough (with good guides to job seaerch like 80000 hours, wait but why, etc.). It needs several tools and integrations: Searching on the web for job postings. a notion board - to list the jobs. a chatbot with memory and a knowledge base to refine your ideas about a suitable job. 

## 3. MVP Scope
 
Input: The user provides one CV and one job posting, either by uploading the CV and pasting the job description or providing a link.
Analysis: The workflow extracts the job’s key requirements and compares them with the experience and skills stated in the CV.
Application materials: It generates:
A tailored cover-letter draft.
Specific suggestions for improving or tailoring the CV for this role, with the relevant job requirements explained.
Human review: The user reviews and edits all generated content. The workflow must not invent experience or submit an application automatically.
Application tracking: The workflow creates a record in one chosen tracker—Google Sheets or Notion—with the company, role, job link, date added, application status, and links to the generated materials. The user updates the status manually.
Basic validation: The workflow checks that the CV and job-posting information are present and reports an error if required input is missing.
 
The user can verify and approve all generated content before using it.


## 4. Risk Assessment



Risk: The LLM misreads a job posting or invents qualifications in CV edits or cover letters.
Probability: Medium · Impact: High
Mitigation: Tell the model to use only information in the posting and CV; request evidence or source snippets for recommendations; label outputs as drafts; require the user to verify every claim before using them.

Risk: A job source or n8n integration fails, changes format, or returns incomplete results.
Probability: Medium · Impact: Medium
Mitigation: Prefer documented APIs or feeds and follow their terms; validate required fields such as title, company, date, and URL; handle failed runs visibly and include the original listing link.

Risk: Searches run slowly or return too many results to process reliably.
Probability: Medium · Impact: Low
Mitigation: Limit the number of results per run, filter by simple criteria before using the LLM, and process large result sets in batches.

Business Risks

Risk: The workflow sends irrelevant or duplicate job recommendations, so the user stops using it.
Probability: Medium · Impact: Medium
Mitigation: Let the user set job title, location, seniority, and other preferences; remove duplicates; provide a way to mark results as relevant or irrelevant and refine filters.

Risk: The workflow is not trusted because it changes application materials without enough user control.
Probability: Medium · Impact: High
Mitigation: Keep the user in control: generate suggestions and drafts only. Do not send applications or make CV changes automatically; require explicit review and approval.

Risk: Costs or setup effort exceed the value of the tool.
Probability: Low · Impact: Medium
Mitigation: Build a small prototype with one source and a limited number of searches. Compare time saved and result usefulness against service costs before adding features.

Risk: Scope grows to include many job sites, dashboards, tracking, interview prep, and automatic applications.
Probability: High · Impact: Medium
Mitigation: Define the MVP as: search one source, filter a small set of postings, create a review-ready application draft for a selected job, and save the result. Defer other features.

Data Risks
Risk: A CV contains personal information that is exposed through the AI provider, workflow logs, or document storage.
Probability: Medium · Impact: High
Mitigation: Send only the information needed; check the privacy and retention terms of each service; restrict access to credentials and stored documents; avoid logging full CV contents; delete data when it is no longer needed.

Risk: Job listings are stale, incomplete, duplicated, or no longer accepting applications.
Probability: Medium · Impact: Medium
Mitigation: Record the source and retrieval date, deduplicate by URL or listing ID, and link to the original posting so the user can confirm it is still open.

Risk: The CV or job posting is inaccurate, outdated, or formatted in a way that causes extraction errors.
Probability: Medium · Impact: Medium
Mitigation: Check that required input fields were extracted; show the parsed job details and proposed CV changes for review; ask the user to correct missing or unclear information rather than guessing.

Risk: Recommendations reflect bias in job descriptions or the model, disadvantaging some candidates or roles.
Probability: Low · Impact: Medium
Mitigation: Use transparent, job-related matching criteria; avoid inferring protected characteristics; show why a role was recommended; let the user review and override rankings.

Highest-priority risks for the MVP: inaccurate application claims, exposure of CV data, and unreliable or stale job listings. Keep a human review step for all application materials and confirm each opportunity at its original source.


## 5. Implementation Plan

Set up the workflow: Choose one input method, such as an n8n form, and one application tracker: Notion or Google Sheets.
Build the MVP: Accept one CV and one job posting; extract key requirements; generate a tailored cover-letter draft and specific CV improvement suggestions.
Save and review: Add the application details and links to the generated materials to the tracker. Keep all materials as drafts for the user to review and approve.
Test and refine: Run sample applications, check the outputs for accuracy, and improve the prompts and error handling.
Future version — job coach: Use materials the user provides, such as their CV, skills, interests, and goals, together with general career knowledge to suggest suitable roles and possible paths toward them. Keep this separate from the MVP; add current job-market research later if needed.

## 6. Success Metrics

A complete input produces a cover-letter draft, CV suggestions, and a tracker entry.

Suggestions are relevant to the job posting and grounded in information from the user’s CV; the user can easily identify and correct anything inaccurate.

The user reviews and approves all application materials before using them.

The workflow completes successfully in at least 4 out of 5 test runs, with errors clearly reported.

In user testing, the workflow saves time compared with preparing and tracking an application manually.