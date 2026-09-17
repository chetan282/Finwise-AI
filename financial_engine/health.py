"""
health.py — a single 0-100 "financial fitness" score, six weighted components.
"""
from dataclasses import dataclass
from models import Profile
from financial_engine.networth import NetWorthResult
from financial_engine.retirement import RetirementResult


@dataclass
class HealthResult:
    score: int
    grade: str
    breakdown: list


def _grade(score: int) -> str:
    if score >= 85: return "Excellent"
    if score >= 70: return "Good"
    if score >= 50: return "Fair"
    if score >= 30: return "Needs work"
    return "Critical"


def compute_health(p: Profile, nw: NetWorthResult, ret: RetirementResult) -> HealthResult:
    rows = []

    pts = min(nw.savings_rate / 0.30, 1) * 25 if nw.savings_rate > 0 else 0
    rows.append(("Savings rate", round(pts), 25,
                 f"{int(nw.savings_rate*100)}% of take-home saved"))

    months = p.liquid_savings / p.monthly_expenses if p.monthly_expenses else 0
    pts = min(months / 6, 1) * 15
    rows.append(("Emergency fund", round(pts), 15,
                 f"{months:.1f} months of expenses in cash"))

    ratio = p.monthly_emi / nw.monthly_take_home if nw.monthly_take_home else 0
    pts = max(0, min(1, (0.50 - ratio) / 0.30)) * 15
    rows.append(("Debt burden", round(pts), 15,
                 f"EMIs are {int(ratio*100)}% of take-home"))

    target = p.annual_salary * 10
    pts = min(p.life_cover / target, 1) * 15 if target else 0
    rows.append(("Life insurance", round(pts), 15,
                 f"cover is {p.life_cover/target:.1f}x of the 10x-income target"))

    pts = min(p.health_cover / 500_000, 1) * 10
    rows.append(("Health insurance", round(pts), 10,
                 f"health cover of Rs {int(p.health_cover):,}"))

    pts = min(ret.on_track_ratio, 1) * 20
    rows.append(("Retirement readiness", round(pts), 20,
                 f"on track for {int(ret.on_track_ratio*100)}% of target corpus"))

    score = int(sum(r[1] for r in rows))
    return HealthResult(score=score, grade=_grade(score), breakdown=rows)
