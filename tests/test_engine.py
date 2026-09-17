"""
test_engine.py — proves the math with known-good checks and a realistic profile.
Run:  python -m tests.test_engine
"""
from models import Profile
from financial_engine import engine
from financial_engine.tax import compute_tax


def test_tax_known_values():
    r = compute_tax(1_275_000)
    assert r.regime == "new" and r.tax == 0, r

    r = compute_tax(2_000_000)
    assert r.regime == "new" and r.tax == 192_400, r

    r = compute_tax(600_000, deductions_80c_80d=150_000)
    assert r.tax == 0, r
    print("  tax checks passed")


def test_full_engine():
    p = Profile(
        age=32, retirement_age=55, life_expectancy=85,
        annual_salary=1_800_000, monthly_expenses=55_000, monthly_emi=25_000,
        existing_investments=800_000, liquid_savings=300_000, other_assets=2_000_000,
        total_liabilities=1_500_000, life_cover=10_000_000, health_cover=1_000_000,
    )
    res = engine.run(p)

    assert res.tax.take_home > 0
    assert res.net_worth.net_worth == 800_000 + 300_000 + 2_000_000 - 1_500_000
    assert res.retirement.corpus_needed > 0
    assert res.retirement.required_sip >= 0
    assert 0 <= res.health.score <= 100
    assert sum(row[1] for row in res.health.breakdown) == res.health.score

    print(f"  regime={res.tax.regime}  tax=Rs{res.tax.tax:,}  "
          f"take-home=Rs{res.net_worth.monthly_take_home:,}/mo")
    print(f"  net worth=Rs{res.net_worth.net_worth:,}  "
          f"surplus=Rs{res.net_worth.monthly_surplus:,}/mo  "
          f"savings rate={int(res.net_worth.savings_rate*100)}%")
    print(f"  corpus needed=Rs{res.retirement.corpus_needed:,}  "
          f"projected=Rs{res.retirement.projected_corpus:,}  "
          f"required SIP=Rs{res.retirement.required_sip:,}/mo")
    print(f"  SWP lasts {res.retirement.swp_lasts_years} yrs  "
          f"(outlives you: {res.retirement.money_outlives_you})")
    print(f"  HEALTH SCORE = {res.health.score}/100 ({res.health.grade})")
    for name, pts, mx, reason in res.health.breakdown:
        print(f"     {name:22s} {pts:>2}/{mx:<2}  — {reason}")


if __name__ == "__main__":
    print("Running FinWise engine tests...\n")
    test_tax_known_values()
    test_full_engine()
    print("\nAll tests passed.")
