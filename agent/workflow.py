import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph


load_dotenv()


class AgentState(TypedDict):
    company_name: str
    job_description: str
    cv_text: str
    report: str


model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
)


def generate_report(state: AgentState):
    prompt = f"""
You are an interview preparation assistant.

Company:
{state["company_name"]}

Job description:
{state["job_description"]}

Candidate CV:
{state["cv_text"]}

Create a concise, personalized interview preparation report with:

1. Role summary
2. Most important job requirements
3. Candidate strengths
4. Possible skill gaps
5. Five likely interview questions
6. Three STAR stories the candidate should prepare
7. Five useful questions to ask the interviewer
8. A seven-day preparation plan

Use only the supplied information.
Do not invent company facts.
Clearly mark information that is unknown.
"""

    response = model.invoke(prompt)

    return {
        "report": response.content
    }


graph_builder = StateGraph(AgentState)

graph_builder.add_node(
    "generate_report",
    generate_report
)

graph_builder.add_edge(
    START,
    "generate_report"
)

graph_builder.add_edge(
    "generate_report",
    END
)

interview_workflow = graph_builder.compile()