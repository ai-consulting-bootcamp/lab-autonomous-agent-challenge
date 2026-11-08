from pydantic import BaseModel
from dotenv import load_dotenv
from workflow import interview_workflow
import os

from fastapi import FastAPI, Header, HTTPException

load_dotenv()

app = FastAPI(title="Interview Preparation Agent")


class InterviewRequest(BaseModel):
    company_name: str
    job_description: str
    cv_text: str


@app.get("/health")
def health_check():
    return {"status": "ok"}
@app.post("/prepare")
@app.post("/prepare")
def prepare_interview(
    request: InterviewRequest,
    x_api_key: str = Header(...),
):
    if x_api_key != os.getenv("APP_API_KEY"):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    result = interview_workflow.invoke(
        {
            "company_name": request.company_name,
            "job_description": request.job_description,
            "cv_text": request.cv_text,
            "report": "",
        }
    )

    return {
        "company_name": result["company_name"],
        "report": result["report"],
    }