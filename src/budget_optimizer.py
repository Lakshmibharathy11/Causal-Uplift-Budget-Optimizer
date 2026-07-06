import numpy as np
import pandas as pd

def compute_tier_roi(segment_df, cost_per_impression=0.01,
                     revenue_per_conversion=1.0):
    """
    Compute expected ROI per confidence tier of Persuadables.
    ROI = (mean_uplift * revenue_per_conversion) / cost_per_impression
    """
    persuadables = segment_df[
        segment_df["segment"] == "Persuadable"
    ].copy()

    tier_stats = persuadables.groupby("confidence").agg(
        user_count=("uplift_score", "count"),
        mean_uplift=("uplift_score", "mean"),
        std_uplift=("uplift_score", "std")
    ).reset_index()

    tier_stats["cost_to_target"] = (
        tier_stats["user_count"] * cost_per_impression
    )
    tier_stats["expected_incremental_conversions"] = (
        tier_stats["user_count"] * tier_stats["mean_uplift"]
    )
    tier_stats["roi"] = (
        tier_stats["expected_incremental_conversions"] *
        revenue_per_conversion /
        tier_stats["cost_to_target"]
    )
    tier_stats["cost_per_incremental_conversion"] = (
        tier_stats["cost_to_target"] /
        tier_stats["expected_incremental_conversions"]
    )

    return tier_stats.sort_values("roi", ascending=False).reset_index(drop=True)


def optimize_budget(tier_stats, total_budget,
                    cost_per_impression=0.01):
    """
    Greedy budget allocation: spend on highest-ROI tier first,
    then next highest, until budget is exhausted.

    Returns allocation DataFrame with spend and
    expected incremental conversions per tier.
    """
    allocation = []
    remaining_budget = total_budget

    for _, row in tier_stats.iterrows():
        tier_cost = row["cost_to_target"]

        if remaining_budget <= 0:
            allocation.append({
                "confidence": row["confidence"],
                "users_targeted": 0,
                "budget_allocated": 0.0,
                "expected_incremental_conversions": 0.0,
                "roi": row["roi"],
                "status": "Not funded"
            })
        elif remaining_budget >= tier_cost:
            # Full tier funded
            remaining_budget -= tier_cost
            allocation.append({
                "confidence": row["confidence"],
                "users_targeted": int(row["user_count"]),
                "budget_allocated": round(tier_cost, 2),
                "expected_incremental_conversions": round(
                    row["expected_incremental_conversions"], 1),
                "roi": round(row["roi"], 3),
                "status": "Fully funded"
            })
        else:
            # Partial tier funded — proportional allocation
            fraction = remaining_budget / tier_cost
            users_partial = int(row["user_count"] * fraction)
            conv_partial = row["expected_incremental_conversions"] * fraction
            allocation.append({
                "confidence": row["confidence"],
                "users_targeted": users_partial,
                "budget_allocated": round(remaining_budget, 2),
                "expected_incremental_conversions": round(conv_partial, 1),
                "roi": round(row["roi"], 3),
                "status": f"Partially funded ({fraction*100:.0f}%)"
            })
            remaining_budget = 0

    alloc_df = pd.DataFrame(allocation)
    alloc_df["cumulative_spend"] = alloc_df["budget_allocated"].cumsum()
    alloc_df["cumulative_conversions"] = (
        alloc_df["expected_incremental_conversions"].cumsum()
    )
    return alloc_df


def do_not_disturb_savings(segment_df, cost_per_impression=0.01):
    """
    Compute budget saved and conversion rate damage avoided
    by explicitly excluding Do Not Disturb users.
    """
    dnd = segment_df[segment_df["segment"] == "DoNotDisturb"]
    users_saved = len(dnd)
    budget_saved = users_saved * cost_per_impression
    conversions_protected = abs(dnd["uplift_score"].sum())

    return {
        "users_excluded": users_saved,
        "budget_saved": round(budget_saved, 2),
        "conversion_rate_damage_avoided": round(conversions_protected, 1)
    }
