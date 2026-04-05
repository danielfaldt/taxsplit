from app.calculator.rules import employer_contribution_rate
from app.calculator.tax import compute_personal_tax, ordinary_base_deduction, total_base_deduction


def test_ordinary_base_deduction_2026_matches_official_example():
    assert ordinary_base_deduction(2026, 120_000) == 37_400


def test_ordinary_base_deduction_2025_matches_official_example():
    assert ordinary_base_deduction(2025, 324_000) == 31_200


def test_personal_tax_2026_is_reasonable_for_mid_income():
    result = compute_personal_tax(year=2026, earned_income=240_000, municipal_rate=32.84)
    assert round(result.base_deduction) == 40_000
    assert 25_000 < result.earned_income_credit < 27_000
    assert 198_000 < result.net_income < 200_000
    assert result.burial_fee_tax > 0


def test_senior_base_deduction_2025_matches_official_example():
    assert total_base_deduction(2025, 90_000, birth_year=1958) == 71_800


def test_senior_personal_tax_gets_higher_base_deduction_and_credit():
    under_66 = compute_personal_tax(year=2026, earned_income=240_000, municipal_rate=32.84, birth_year=1985)
    over_66 = compute_personal_tax(year=2026, earned_income=240_000, municipal_rate=32.84, birth_year=1959)

    assert over_66.base_deduction > under_66.base_deduction
    assert over_66.total_tax < under_66.total_tax
    assert over_66.net_income > under_66.net_income


def test_2025_employer_contribution_rate_uses_year_specific_age_threshold():
    assert employer_contribution_rate(2025, 1958) == 0.1021
    assert employer_contribution_rate(2025, 1959) == 0.3142


def test_local_income_tax_credit_is_not_affected_by_church_or_burial_fee():
    without_extra_fees = compute_personal_tax(
        year=2026,
        earned_income=300_000,
        municipal_rate=32.80,
        burial_fee_rate=0.0,
        church_fee_rate=0.0,
        birth_year=1985,
    )
    with_extra_fees = compute_personal_tax(
        year=2026,
        earned_income=300_000,
        municipal_rate=32.80,
        burial_fee_rate=0.292,
        church_fee_rate=1.00,
        birth_year=1985,
    )

    expected_extra_tax = round(with_extra_fees.taxable_income * 0.01292, 2)

    assert with_extra_fees.earned_income_credit == without_extra_fees.earned_income_credit
    assert with_extra_fees.pension_credit == without_extra_fees.pension_credit
    assert round(with_extra_fees.total_tax - without_extra_fees.total_tax, 2) == expected_extra_tax
