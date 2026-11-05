# Writes one lead to the Airtable "Leads" table (same 20 fields as the n8n workflow)
import os, datetime
from pyairtable import Api


def save_lead(lead, out, source):
    r = out["result"]
    form_name = lead.get("Business name", "Not stated")
    form_category = lead.get("Business category", "Not stated")
    fields = {
        "Submitted at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "Source": source,
        "Business name": form_name if form_name != "Not stated" else r.business_name,  # form value wins
        "Contact name": lead.get("Contact name", ""),
        "Contact email": lead.get("Contact email", ""),
        "Category": form_category if form_category != "Not stated" else r.category,
        "Listing volume": int(lead.get("Listings per month") or r.listing_volume or 0),
        "Need": r.need,
        "Budget": r.budget,
        "Timeline": r.timeline,
        "Inquiry": lead.get("Inquiry", ""),
        "Lead score": r.lead_score,
        "Rating": r.rating,
        "Score reason": r.score_reason,
        "Sales team": r.sales_team,
        "Next action": out["next_action"],
        "Drafted reply": r.drafted_reply,
        "KB sources": ", ".join(r.kb_sources),
        "Consent": bool(lead.get("Consent")),
        "Execution ID": out["run_id"],
    }
    fields = {k: v for k, v in fields.items() if v != ""}  # Airtable rejects empty emails
    table = Api(os.getenv("AIRTABLE_TOKEN")).table(os.getenv("AIRTABLE_BASE_ID"), os.getenv("AIRTABLE_TABLE", "Leads"))
    return table.create(fields, typecast=True)
