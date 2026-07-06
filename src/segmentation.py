import numpy as np
import pandas as pd

def compute_thresholds(uplift_scores, cost_per_impression=0.01,
                       revenue_per_conversion=1.0):
    """
    Derive statistically grounded segmentation thresholds.

    Positive threshold: break-even uplift
        minimum uplift needed for the ad to pay for itself
        = cost_per_impression / revenue_per_conversion

    Negative threshold: symmetric around zero
        users below this are actively harmed by the ad
    """
    positive_threshold = cost_per_impression / revenue_per_conversion
    negative_threshold = -positive_threshold

    return {
        'positive': round(positive_threshold, 4),
        'negative': round(negative_threshold, 4)
    }


def assign_segments(uplift_scores, positive_threshold=0.01,
                    negative_threshold=-0.01):
    """
    Assign each user to one of four business segments.

    Returns a DataFrame with:
    - segment: Persuadable / Neutral_SureThing /
               Neutral_LostCause / DoNotDisturb
    - confidence: High / Medium / Low within each segment
    - uplift_score: raw score for reference
    """
    scores = np.array(uplift_scores)
    n = len(scores)

    segments = np.where(
        scores > positive_threshold, "Persuadable",
        np.where(
            scores < negative_threshold, "DoNotDisturb",
            np.where(scores >= 0, "Neutral_SureThing",
                                  "Neutral_LostCause")
        )
    )

    # Confidence tiers within each segment
    # Based on distance from the threshold boundary
    confidence = []
    for score, seg in zip(scores, segments):
        if seg == "Persuadable":
            if score > positive_threshold * 5:
                confidence.append("High")
            elif score > positive_threshold * 2:
                confidence.append("Medium")
            else:
                confidence.append("Low")
        elif seg == "DoNotDisturb":
            if score < negative_threshold * 5:
                confidence.append("High")
            elif score < negative_threshold * 2:
                confidence.append("Medium")
            else:
                confidence.append("Low")
        else:
            confidence.append("Low")

    return pd.DataFrame({
        'uplift_score': scores,
        'segment': segments,
        'confidence': confidence
    })


def segment_summary(segment_df):
    """
    Business-readable summary of segment distribution.
    Returns a DataFrame with counts, percentages,
    and mean uplift per segment and confidence tier.
    """
    summary = segment_df.groupby(
        ["segment", "confidence"]
    ).agg(
        count=("uplift_score", "count"),
        mean_uplift=("uplift_score", "mean"),
        std_uplift=("uplift_score", "std")
    ).reset_index()

    total = len(segment_df)
    summary["pct_of_total"] = (summary["count"] / total * 100).round(1)
    summary["mean_uplift"] = summary["mean_uplift"].round(6)
    summary["std_uplift"] = summary["std_uplift"].round(6)

    return summary.sort_values(
        ["segment", "confidence"],
        ascending=[True, False]
    ).reset_index(drop=True)
