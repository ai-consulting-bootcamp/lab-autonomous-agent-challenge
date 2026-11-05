# Qualifies one lead: guard → retrieve → rerank → LLM → check
import os, time, uuid, json
import cohere
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from src.prompts import SYSTEM_PROMPT, USER_TEMPLATE, LeadResult, ScoreBreakdown, PROMPT_VERSION

MAX_INQUIRY_CHARS = 2000
INJECTION_PHRASES = ["ignore your", "ignore all", "ignore previous", "rate this lead", "rate me", "score 100", "system prompt"]
_clients = {}


def get_clients():
    # Create the API clients once and reuse them
    if not _clients:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=512)  # same as n8n and the notebook
        _clients["store"] = PineconeVectorStore(index_name=os.getenv("PINECONE_INDEX", "kleinanzeigen-business-kb"),
                                                embedding=embeddings)
        _clients["llm"] = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini")).with_structured_output(LeadResult)
        _clients["cohere"] = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
    return _clients


def rating_for(score):
    # Same thresholds as the prompt
    if score >= 70:
        return "Hot"
    if score >= 40:
        return "Warm"
    return "Cold"


def needs_review(lead, reason):
    # Result used for the input guard and for errors (no LLM call needed)
    return LeadResult(business_name=lead.get("Business name", "Not stated"), category=lead.get("Business category", "Not stated"),
                      listing_volume=0, need="Not stated", budget="Not stated", timeline="Not stated",
                      score_breakdown=ScoreBreakdown(category=0, volume=0, need=0, timeline=0, budget=0),
                      lead_score=0, rating="Needs review", score_reason=reason, sales_team="Sales manager",
                      drafted_reply="", kb_sources=[])


def retrieve(lead):
    # Search Pinecone, rerank with Cohere (one call per lead: trial key allows 10 per minute), keep the top 5
    c = get_clients()
    query = f"{lead.get('Business category', '')} {lead.get('Inquiry', '')}"
    docs = [d.page_content for d in c["store"].similarity_search(query, k=10)]
    ranked = c["cohere"].rerank(model=os.getenv("COHERE_RERANK_MODEL", "rerank-v3.5"), query=query, documents=docs, top_n=5)
    return [docs[r.index] for r in ranked.results]


def check(result):
    # Private seller rule, applied in code: no points for category, volume and need
    if result.sales_team == "None (self-service)" and result.rating != "Needs review":
        b = result.score_breakdown
        b.category = b.volume = b.need = 0
        result.lead_score = sum(b.model_dump().values())
        result.rating = rating_for(result.lead_score)
        result.score_reason += " [Private seller rule applied in code]"
    # Score must equal the breakdown sum and the rating must match the thresholds
    total = sum(result.score_breakdown.model_dump().values())
    if result.rating != "Needs review" and (total != result.lead_score or result.rating != rating_for(total)):
        result.score_reason += f" [Check failed: breakdown sum {total}, score {result.lead_score}, rating {result.rating}]"
        result.rating = "Needs review"
        result.sales_team = "Sales manager"
    return result


def next_action(result):
    actions = {"Hot": f"Hot: hand to {result.sales_team}",
               "Warm": "Warm: rep sends drafted follow-up question",
               "Cold": "Cold: rep sends drafted self-service reply",
               "Needs review": "Needs review: sales manager checks"}
    return actions[result.rating]


def qualify(lead):
    # Main entry point: returns the result plus run details for logging
    run_id = "gradio-" + uuid.uuid4().hex[:8]
    start = time.time()
    inquiry = (lead.get("Inquiry") or "").strip()
    chunks = []
    if not inquiry or len(inquiry) > MAX_INQUIRY_CHARS:
        result = needs_review(lead, "Input guard: inquiry empty or longer than 2,000 characters. No LLM call.")
    elif any(p in inquiry.lower() for p in INJECTION_PHRASES):
        result = needs_review(lead, "Input guard: inquiry contains instructions to the AI. No LLM call.")
    else:
        try:
            try:
                chunks = retrieve(lead)
            except Exception:
                time.sleep(7)  # retry once, e.g. after a rate limit
                chunks = retrieve(lead)
            prompt = USER_TEMPLATE.format(business_name=lead.get("Business name", "Not stated"),
                                          contact_name=lead.get("Contact name", "Not stated"),
                                          category=lead.get("Business category", "Not stated"),
                                          listings=lead.get("Listings per month") or "Not stated",
                                          inquiry=inquiry, kb="\n\n---\n\n".join(chunks))
            result = check(get_clients()["llm"].invoke([("system", SYSTEM_PROMPT), ("human", prompt)]))
        except Exception as e:
            result = needs_review(lead, f"Agent error: {type(e).__name__}: {e}")
    seconds = round(time.time() - start, 1)
    # One log line per lead: visible in the terminal and in Render logs (monitoring)
    print(json.dumps({"run_id": run_id, "rating": result.rating, "score": result.lead_score,
                      "team": result.sales_team, "seconds": seconds, "prompt": PROMPT_VERSION}))
    return {"result": result, "next_action": next_action(result), "run_id": run_id,
            "seconds": seconds, "chunks": chunks}
