"""
retirement.py — corpus needed, required SIP, SWP sustainability check.
"""
from dataclasses import dataclass
from models import Profile


@dataclass
class RetirementResult:
    corpus_needed: float
    projected_corpus: float
    required_sip: float
    on_track_ratio: float
    swp_lasts_years: int
    money_outlives_you: bool


def _fv_annuity(monthly: float, annual_rate: float, years: int) -> float:
    r, n = annual_rate / 12, years * 12
    if r == 0:
        return monthly * n
    return monthly * (((1 + r) ** n - 1) / r)


def _required_sip(target: float, annual_rate: float, years: int) -> float:
    r, n = annual_rate / 12, years * 12
    if n == 0:
        return target
    if r == 0:
        return target / n
    return target * r / ((1 + r) ** n - 1)


def compute_retirement(p: Profile, current_monthly_sip: float) -> RetirementResult:
    years = p.years_to_retire()

    annual_expense = p.monthly_expenses * 12
    future_expense = annual_expense * (1 + p.inflation) ** years
    corpus_needed = future_expense * p.fire_multiplier

    grown_existing = p.existing_investments * (1 + p.return_pre_retire) ** years
    grown_sip = _fv_annuity(current_monthly_sip, p.return_pre_retire, years)
    projected = grown_existing + grown_sip

    gap = max(corpus_needed - grown_existing, 0)
    required_sip = round(_required_sip(gap, p.return_pre_retire, years))

    corpus = corpus_needed
    monthly_spend = future_expense / 12
    r_post = p.return_post_retire / 12
    lasted = 0
    for yr in range(p.retirement_years()):
        for _ in range(12):
            corpus = corpus * (1 + r_post) - monthly_spend
            if corpus <= 0:
                break
        if corpus <= 0:
            break
        monthly_spend *= (1 + p.inflation)
        lasted = yr + 1

    return RetirementResult(
        corpus_needed=round(corpus_needed),
        projected_corpus=round(projected),
        required_sip=required_sip,
        on_track_ratio=round(projected / corpus_needed, 2) if corpus_needed else 0,
        swp_lasts_years=lasted,
        money_outlives_you=lasted >= p.retirement_years(),
    )
