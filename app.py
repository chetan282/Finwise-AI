"""
app.py — FinWise AI dashboard (Streamlit).
Run:  streamlit run app.py
"""
import os
import streamlit as st
from dotenv import load_dotenv

from models import Profile
from financial_engine import engine

load_dotenv()
st.set_page_config(page_title="FinWise AI", page_icon="\U0001F4B0", layout="wide")
st.title("\U0001F4B0 FinWise AI — your money, one clear picture")


def rupees(label, value, step=10_000):
    return st.sidebar.number_input(label, min_value=0, value=value, step=step)

st.sidebar.header("Your details")
age = st.sidebar.slider("Current age", 18, 70, 32)
ret_age = st.sidebar.slider("Retirement age", age + 1, 75, max(age + 1, 55))
salary = rupees("Annual gross salary (Rs)", 1_800_000, 50_000)
expenses = rupees("Monthly expenses (Rs)", 55_000, 5_000)
emi = rupees("Monthly loan EMIs (Rs)", 25_000, 5_000)

st.sidebar.subheader("Assets & liabilities")
investments = rupees("Investments — MF/stocks/PPF (Rs)", 800_000, 50_000)
liquid = rupees("Cash / FD / emergency fund (Rs)", 300_000, 25_000)
other = rupees("Other assets — property/gold (Rs)", 2_000_000, 100_000)
liabilities = rupees("Total outstanding loans (Rs)", 1_500_000, 100_000)

st.sidebar.subheader("Insurance")
life = rupees("Term life cover (Rs)", 10_000_000, 500_000)
health = rupees("Health cover (Rs)", 1_000_000, 100_000)

st.sidebar.subheader("Old-regime deductions")
deductions = rupees("80C + 80D + HRA total (Rs)", 150_000, 25_000)

p = Profile(
    age=age, retirement_age=ret_age, annual_salary=salary,
    monthly_expenses=expenses, monthly_emi=emi, existing_investments=investments,
    liquid_savings=liquid, other_assets=other, total_liabilities=liabilities,
    life_cover=life, health_cover=health,
)
r = engine.run(p, deductions)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Health score", f"{r.health.score}/100", r.health.grade)
c2.metric("Net worth", f"Rs {r.net_worth.net_worth:,}")
c3.metric("Monthly surplus", f"Rs {r.net_worth.monthly_surplus:,}",
          f"{int(r.net_worth.savings_rate*100)}% saved")
c4.metric("Best tax regime", r.tax.regime.upper(), f"tax Rs {r.tax.tax:,}")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("\U0001F3C6 Financial health breakdown")
    for name, pts, mx, reason in r.health.breakdown:
        st.write(f"**{name}** — {pts}/{mx}")
        st.progress(pts / mx)
        st.caption(reason)

with right:
    st.subheader("\U0001F9FE Tax")
    st.write(f"New regime: **Rs {r.tax.new_tax:,}**  |  Old regime: **Rs {r.tax.old_tax:,}**")
    st.success(f"Pick **{r.tax.regime.upper()}** — you save "
               f"Rs {abs(r.tax.new_tax - r.tax.old_tax):,}.")

    st.subheader("\U0001F3D6\uFE0F Retirement")
    st.write(f"Corpus needed at {ret_age}: **Rs {r.retirement.corpus_needed:,}**")
    st.write(f"On current savings you'll reach: **Rs {r.retirement.projected_corpus:,}** "
             f"({int(r.retirement.on_track_ratio*100)}% of target)")
    st.write(f"SIP needed to hit target: **Rs {r.retirement.required_sip:,}/mo**")
    if r.retirement.money_outlives_you:
        st.success(f"Your corpus lasts all {p.retirement_years()} retirement years. \u2705")
    else:
        st.warning(f"Corpus runs out after {r.retirement.swp_lasts_years} years — "
                   f"raise your SIP or trim retirement expenses.")

st.divider()

st.subheader("\U0001F4AC Ask FinWise for a plan")
if st.button("Generate my action plan"):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("Set ANTHROPIC_API_KEY in your .env file to enable AI advice.")
    else:
        try:
            from advisor.advisor import get_advice
            with st.spinner("Thinking through your numbers..."):
                st.markdown(get_advice(p, r))
        except FileNotFoundError:
            st.error("Knowledge index missing. Run:  python -m rag.build_index")

st.caption("Educational tool, not SEBI-registered investment advice. Tax rules: FY 2025-26.")
