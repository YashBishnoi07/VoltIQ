"""Statistical hypothesis testing for EV charging demand patterns."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class TestResult:
    test_name: str
    statistic: float
    p_value: float
    effect_size: float
    effect_size_label: str
    significant: bool
    interpretation: str
    group_a_label: str
    group_b_label: str
    group_a_mean: float
    group_b_mean: float


def test_normality(series: pd.Series, name: str = "variable") -> dict[str, object]:
    """Shapiro-Wilk (n ≤ 5000) or KS-test for normality."""
    data = series.dropna().values
    n = len(data)

    if n <= 5000:
        stat, p = stats.shapiro(data)
        test = "Shapiro-Wilk"
    else:
        # KS test against a fitted normal for large samples
        mu, sigma = data.mean(), data.std()
        stat, p = stats.kstest(data, "norm", args=(mu, sigma))
        test = "Kolmogorov-Smirnov"

    return {
        "variable": name,
        "test": test,
        "n": n,
        "statistic": round(float(stat), 6),
        "p_value": round(float(p), 6),
        "is_normal": bool(p > 0.05),
        "interpretation": (
            f"At α=0.05, the distribution of {name} is "
            + ("approximately normal." if p > 0.05 else "NOT normal (use non-parametric tests).")
        ),
    }


def test_weekday_vs_weekend(hourly_df: pd.DataFrame) -> TestResult:
    """Mann-Whitney U test: weekday vs weekend sessions per hour."""
    weekday = hourly_df.loc[hourly_df["is_weekend"] == 0, "sessions_per_hour"].dropna().values
    weekend = hourly_df.loc[hourly_df["is_weekend"] == 1, "sessions_per_hour"].dropna().values

    stat, p = stats.mannwhitneyu(weekday, weekend, alternative="two-sided")

    # Rank-biserial correlation as effect size for Mann-Whitney
    n1, n2 = len(weekday), len(weekend)
    r = 1 - (2 * stat) / (n1 * n2)
    effect_label = _interpret_r(abs(r))

    return TestResult(
        test_name="Mann-Whitney U",
        statistic=round(float(stat), 4),
        p_value=round(float(p), 6),
        effect_size=round(float(r), 4),
        effect_size_label=effect_label,
        significant=bool(p < 0.05),
        interpretation=(
            f"Weekday demand (mean={weekday.mean():.2f}) vs weekend demand "
            f"(mean={weekend.mean():.2f}). Effect size r={r:.3f} ({effect_label}). "
            + ("Significant difference." if p < 0.05 else "No significant difference.")
        ),
        group_a_label="Weekday",
        group_b_label="Weekend",
        group_a_mean=round(float(weekday.mean()), 4),
        group_b_mean=round(float(weekend.mean()), 4),
    )


def test_peak_hours_anova(hourly_df: pd.DataFrame) -> dict[str, object]:
    """Kruskal-Wallis H test across all 24 hour groups (non-parametric ANOVA)."""
    groups = [
        hourly_df.loc[hourly_df["hour"] == h, "sessions_per_hour"].dropna().values
        for h in range(24)
    ]
    # Drop hours with no data
    groups = [g for g in groups if len(g) > 0]

    stat, p = stats.kruskal(*groups)

    # Eta-squared approximation for Kruskal-Wallis
    n_total = sum(len(g) for g in groups)
    eta_sq = (stat - len(groups) + 1) / (n_total - len(groups))

    return {
        "test": "Kruskal-Wallis H",
        "statistic": round(float(stat), 4),
        "p_value": round(float(p), 6),
        "df": len(groups) - 1,
        "eta_squared": round(float(eta_sq), 4),
        "significant": bool(p < 0.05),
        "interpretation": (
            f"H({len(groups)-1}) = {stat:.2f}, p = {p:.4f}. "
            f"Eta² = {eta_sq:.3f} ({'large' if eta_sq > 0.14 else 'medium' if eta_sq > 0.06 else 'small'} effect). "
            + ("Hour-of-day significantly affects demand." if p < 0.05 else "No significant hour effect.")
        ),
    }


def compute_confidence_interval(
    series: pd.Series, confidence: float = 0.95
) -> tuple[float, float]:
    """Bootstrap 95% CI for the mean."""
    data = series.dropna().values
    n = len(data)
    se = stats.sem(data)
    h = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    mean = data.mean()
    return round(float(mean - h), 4), round(float(mean + h), 4)


def location_type_comparison(hourly_df: pd.DataFrame) -> dict[str, object]:
    """Kruskal-Wallis across urban/suburban/highway/rural station demand."""
    groups = {
        loc: hourly_df.loc[hourly_df["location_type"] == loc, "sessions_per_hour"]
        .dropna()
        .values
        for loc in hourly_df["location_type"].unique()
    }
    valid_groups = {k: v for k, v in groups.items() if len(v) > 1}

    stat, p = stats.kruskal(*valid_groups.values())

    return {
        "test": "Kruskal-Wallis H (location type)",
        "statistic": round(float(stat), 4),
        "p_value": round(float(p), 6),
        "significant": bool(p < 0.05),
        "group_means": {k: round(float(v.mean()), 4) for k, v in valid_groups.items()},
        "interpretation": (
            "Location type significantly affects demand." if p < 0.05 else "No significant location effect."
        ),
    }


def _interpret_r(r: float) -> str:
    if r < 0.1:
        return "negligible"
    if r < 0.3:
        return "small"
    if r < 0.5:
        return "medium"
    return "large"
