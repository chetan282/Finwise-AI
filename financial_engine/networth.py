"""
networth.py — assets minus liabilities, plus monthly cashflow.
"""
from dataclasses import dataclass
from models import Profile


@dataclass
class NetWorthResult:
    total_assets: float
    net_worth: float
    monthly_take_home: float
    monthly_surplus: float
    savings_rate: float


def compute_net_worth(p: Profile, annual_take_home: float) -> NetWorthResult:
    total_assets = p.existing_investments + p.liquid_savings + p.other_assets
    net_worth = total_assets - p.total_liabilities

    take_home_m = annual_take_home / 12
    surplus = take_home_m - p.monthly_expenses - p.monthly_emi
    savings_rate = surplus / take_home_m if take_home_m else 0

    return NetWorthResult(
        total_assets=round(total_assets),
        net_worth=round(net_worth),
        monthly_take_home=round(take_home_m),
        monthly_surplus=round(surplus),
        savings_rate=round(savings_rate, 2),
    )
