## 1. Use Case

### Use Case Name

Interview Preparation Report Agent

### Problem Statement

Preparing for a job interview requires candidates to review the job advertisement, understand the main requirements, compare them with their CV, and organize useful interview notes. This process is time-consuming, and important information can easily be missed.

The proposed agent analyzes the supplied job description and CV and generates a structured, personalized interview preparation report.

### Target Users

The primary users are job seekers who have an upcoming interview and need a fast, structured, and personalized preparation report.

### Current Manual Process

The job seeker studies the job requirements, reviews their CV, identifies relevant experience, prepares interview questions, and organizes the findings into interview notes. This can take between 60 and 90 minutes for each application.

### MVP Agent Behavior

The user provides:

- Company name
- Full job description
- CV text

The agent analyzes only the supplied information. It extracts the main job requirements, compares them with the candidate’s experience, identifies possible gaps, and generates a personalized interview preparation report.

The current MVP does not browse the web or research recent company news.

### Verification Criteria

The MVP is working correctly when:

1. It produces a readable and structured interview preparation report.
2. The main requirements are extracted from the supplied job description.
3. Candidate strengths are supported by information from the supplied CV.
4. Missing information is marked as unknown instead of being invented.
5. Requests without the correct API key are rejected.
6. The workflow completes one successful execution from input to final report.

### Technical Behavior

When the workflow starts, n8n prepares the company name, job description, and CV text. It sends these values to a secured FastAPI endpoint.

FastAPI validates the application API key and invokes the LangGraph workflow. LangGraph sends the supplied information to the OpenAI model and returns the generated report to n8n.

## Implementation Evidence

### Implemented Workflow

The working prototype uses n8n for external orchestration and LangGraph for the AI workflow.

1. The n8n Manual Trigger starts the workflow.
2. The Prepare Input node creates the company name, job description, and CV text.
3. The Generate Interview Report node sends a secured HTTP POST request to the FastAPI endpoint.
4. FastAPI validates the API key and passes the input to the LangGraph workflow.
5. LangGraph invokes the OpenAI model to generate the personalized interview preparation report.
6. The generated report is returned to n8n.

### Implemented Architecture

- **n8n:** Starts the process, prepares the input, and calls the API.
- **FastAPI:** Provides the `/health` and `/prepare` endpoints.
- **LangGraph:** Manages the report-generation workflow.
- **OpenAI:** Analyzes the supplied job and CV information and generates the report.
- **Cloudflare Quick Tunnel:** Temporarily makes the local FastAPI server accessible to n8n.

### Successful Test

The complete workflow was executed successfully using test data for a Product Manager role at n8n.

The final response contained:

- Company name
- Role summary
- Important job requirements
- Candidate strengths
- Possible skill gaps
- Likely interview questions
- Suggested STAR stories
- Questions for the interviewer
- Seven-day preparation plan

### Security Controls

- The OpenAI API key and application API key are stored in `.env`.
- The `.env` file is excluded through `.gitignore`.
- The FastAPI `/prepare` endpoint requires an `x-api-key` header.
- n8n stores the application API key in a Header Auth credential instead of the exported workflow.

### Current Limitations

- The input is currently entered manually in the n8n workflow.
- The Cloudflare Quick Tunnel URL is temporary.
- The current LangGraph implementation contains one report-generation node.
- The generated report is returned to n8n but is not stored in a database.
- External company research and source citations are not implemented.

### Possible Future Improvements

- Replace the manual trigger with a form or webhook.
- Add company and recent-news research tools.
- Add source citations to company information.
- Expand LangGraph into separate analysis, comparison, generation, and review nodes.
- Store or deliver the final report through Notion, email, or another output channel.