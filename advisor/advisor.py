"""
advisor.py — turns numbers into words, grounded by RAG.
"""
import os
from anthropic import Anthropic
from models import Profile
from financial_engine.engine import Results
from rag.retriever import retrieve

MODEL = "claude-sonnet-5"

SYSTEM = (
    "You are FinWise, a blunt, numbers-driven personal finance coach for salaried "
    "Indians. Give a short, prioritized action plan: what to fix first, second, third. "
    "Use rupees and be specific with amounts. Base every claim on the CONTEXT provided; "
    "do not invent tax rules or numbers. End with one honest sentence on the single "
    "biggest lever for this person. You are not a SEBI-registered advisor; this is "
    "educational, not a recommendation to buy any specific product."
)


def _facts(p: Profile, r: Results) -> str:
    return f"""USER NUMBERS
Age {p.age}, retiring at {p.retirement_age}.
Gross salary: Rs {p.annual_salary:,}/yr. Recommended regime: {r.tax.regime} (tax Rs {r.tax.tax:,}).
Take-home: Rs {r.net_worth.monthly_take_home:,}/mo. Monthly surplus: Rs {r.net_worth.monthly_surplus:,} ({int(r.net_worth.savings_rate*100)}% savings rate).
Net worth: Rs {r.net_worth.net_worth:,}.
Retirement corpus needed: Rs {r.retirement.corpus_needed:,}. Projected: Rs {r.retirement.projected_corpus:,} ({int(r.retirement.on_track_ratio*100)}% of target).
Required SIP to hit target: Rs {r.retirement.required_sip:,}/mo.
Life cover Rs {p.life_cover:,} (target ~10x salary). Health cover Rs {p.health_cover:,}.
Health score: {r.health.score}/100 ({r.health.grade}).
Weakest areas: {', '.join(n for n,pts,mx,_ in r.health.breakdown if pts < mx*0.6) or 'none'}."""


def get_advice(p: Profile, r: Results) -> str:
    query = "tax regime, retirement SIP, insurance cover, investment priority for salaried"
    context = "\n\n".join(f"[{c['source']}] {c['text']}" for c in retrieve(query, k=6))

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model=MODEL,
        max_tokens=16000,  # thinking tokens count toward this; billed only for what's used
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": f"CONTEXT (financial knowledge):\n{context}\n\n{_facts(p, r)}\n\n"
                       f"Write my prioritized action plan.",
        }],
    )
    # content can start with a ThinkingBlock; keep only the text blocks
    text = "".join(b.text for b in msg.content if b.type == "text").strip()
    if not text:
        return f"Couldn't generate advice right now (stop reason: {msg.stop_reason}). Please try again."
    return text
