"""
engine.py — runs the whole financial engine in dependency order.
"""
from dataclasses import dataclass
from models import Profile
from financial_engine.tax import compute_tax, TaxResult
from financial_engine.networth import compute_net_worth, NetWorthResult
from financial_engine.retirement import compute_retirement, RetirementResult
from financial_engine.health import compute_health, HealthResult


@dataclass
class Results:
    tax: TaxResult
    net_worth: NetWorthResult
    retirement: RetirementResult
    health: HealthResult


def run(p: Profile, deductions: float = 0) -> Results:
    tax = compute_tax(p.annual_salary, deductions)
    nw = compute_net_worth(p, tax.take_home)
    current_sip = max(nw.monthly_surplus, 0)
    ret = compute_retirement(p, current_sip)
    health = compute_health(p, nw, ret)
    return Results(tax=tax, net_worth=nw, retirement=ret, health=health)
