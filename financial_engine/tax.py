"""
tax.py — Indian income tax, FY 2025-26 / AY 2026-27.
"""
from dataclasses import dataclass

NEW_SLABS = [(400_000, 0.0), (800_000, 0.05), (1_200_000, 0.10),
             (1_600_000, 0.15), (2_000_000, 0.20), (2_400_000, 0.25),
             (None, 0.30)]

OLD_SLABS = [(250_000, 0.0), (500_000, 0.05), (1_000_000, 0.20),
             (None, 0.30)]

CESS = 0.04


@dataclass
class TaxResult:
    regime: str
    taxable_income: float
    tax: float
    take_home: float
    new_tax: float
    old_tax: float


def _slab_tax(taxable: float, slabs) -> float:
    tax, lower = 0.0, 0.0
    for upper, rate in slabs:
        cap = upper if upper is not None else taxable
        if taxable > lower:
            tax += (min(taxable, cap) - lower) * rate
            lower = cap
        else:
            break
    return tax


def _regime_tax(gross_salary: float, deductions: float, slabs,
                 std_deduction: float, rebate_limit: float, rebate_cap: float) -> float:
    taxable = max(gross_salary - std_deduction - deductions, 0)
    base = _slab_tax(taxable, slabs)
    if taxable <= rebate_limit:
        base = max(base - rebate_cap, 0)
    return round(base * (1 + CESS))


def compute_tax(annual_salary: float, deductions_80c_80d: float = 0) -> TaxResult:
    new_tax = _regime_tax(annual_salary, 0, NEW_SLABS,
                           std_deduction=75_000, rebate_limit=1_200_000, rebate_cap=60_000)
    old_tax = _regime_tax(annual_salary, deductions_80c_80d, OLD_SLABS,
                           std_deduction=50_000, rebate_limit=500_000, rebate_cap=12_500)

    if new_tax <= old_tax:
        regime, tax, std, ded = "new", new_tax, 75_000, 0
    else:
        regime, tax, std, ded = "old", old_tax, 50_000, deductions_80c_80d

    taxable = max(annual_salary - std - ded, 0)
    return TaxResult(regime=regime, taxable_income=taxable, tax=tax,
                      take_home=round(annual_salary - tax),
                      new_tax=new_tax, old_tax=old_tax)
