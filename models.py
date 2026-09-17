"""
models.py — One dataclass that holds everything a user tells us.
"""
from dataclasses import dataclass, field


@dataclass
class Profile:
    # --- Personal ---
    age: int = 30
    retirement_age: int = 55
    life_expectancy: int = 85

    # --- Income & spending (annual salary is GROSS, per year) ---
    annual_salary: float = 1_200_000
    monthly_expenses: float = 40_000
    monthly_emi: float = 0

    # --- What you own & owe ---
    existing_investments: float = 0
    liquid_savings: float = 0
    other_assets: float = 0
    total_liabilities: float = 0

    # --- Protection ---
    life_cover: float = 0
    health_cover: float = 0

    # --- Assumptions ---
    inflation: float = 0.06
    return_pre_retire: float = 0.12
    return_post_retire: float = 0.08
    fire_multiplier: float = 30

    def years_to_retire(self) -> int:
        return max(self.retirement_age - self.age, 0)

    def retirement_years(self) -> int:
        return max(self.life_expectancy - self.retirement_age, 0)
