# 📡 Causal Uplift Intelligence Platform

> **Who converts because of your ad — and who would have anyway?**

[![Demo Video](https://img.shields.io/badge/Watch-Demo%20Video-red?logo=youtube)](https://youtu.be/QV7yTNwBOlk)
[![GitHub](https://img.shields.io/badge/View-Source%20Code-black?logo=github)](https://github.com/Lakshmibharathy11/Causal-Uplift-Budget-Optimizer)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![AWS](https://img.shields.io/badge/Deployed-AWS%20EC2-orange?logo=amazon-aws)](https://aws.amazon.com)

---

## The Business Problem

Most advertising platforms report impressive numbers — clicks, impressions, conversions. But they share one critical flaw: they cannot tell the difference between a conversion **caused by** your ad and a conversion that would have happened **anyway**.

Imagine sending a discount email to 100,000 users. 8,000 of them buy. Your platform reports 8,000 conversions. But how many would have bought without ever seeing the email? If 6,000 of them were already planning to purchase, your ad only moved 2,000 people — and you wasted budget on the other 6,000.

**This pipeline solves that problem using causal inference — not correlation.**

---

## What This Pipeline Does

It analyzes every user in your audience and classifies them into four groups:

| Segment | Who they are | What to do |
|---|---|---|
|  **Persuadable** (13.2%) | Converts *because of* the ad | **Target these — your real ROI** |
| ✓ **Sure Thing** (77.9%) | Converts regardless of the ad | Skip — wasted spend |
| — **Lost Cause** (7.4%) | Never converts, ad or no ad | Skip — nothing works |
| **Do Not Disturb** (1.5%) | Less likely to convert *with* the ad | **Explicitly exclude** |

Then it recommends exactly how much to spend on each group, and translates everything into plain-English executive guidance using a verified LLM advisor.

---

## Key Results

| Metric | Value | What it means |
|---|---|---|
| **Model quality (Qini)** | 0.726 | 72.6% of the way from random to perfect targeting |
| **Lift at top 30%** | 87.8% | Target 30% of users, capture 87.8% of all incremental conversions |
| **Calibration error** | 0.000065 | Predicted uplift matches actual observed uplift to within 0.007% |
| **Budget ceiling** | $736.67 | Optimal spend — beyond this, zero additional lift |
| **High-tier ROI** | 15.6x | $1 spent on top Persuadables returns $15.60 in incremental value |
| **DND conversions protected** | 652 | Conversions saved by excluding Do Not Disturb users |

---

## Dataset

**Criteo Uplift Modeling Dataset v2.1** — a real-world advertising incrementality experiment published by Criteo AI Lab.

| Property | Value |
|---|---|
| Total users | 13,979,592 |
| Experiment period | 2021 |
| Treatment group | 85% (shown ads) |
| Control group | 15% (ads withheld — holdout) |
| Features | 12 anonymized behavioral signals (f0-f11) |
| Primary outcome | Visit (did user visit site after experiment?) |
| Secondary outcome | Conversion (did user purchase?) |

**Why this dataset matters for causal inference**: treatment was randomly assigned — meaning the only systematic difference between users who saw ads and users who did not is the ad itself. We verified this with Standardized Mean Difference (SMD) checks across all 12 features (max SMD: 0.047, well below the 0.1 threshold).

---

## Pipeline Architecture

Layer 1 - Data Validation
Randomization check (SMD) · all 12 features balanced
Stratified 20% sample · 2.8M rows · proportions preserved

Layer 2 - Uplift Estimation
T-Learner (XGBoost) · Transformed Outcome · X-Learner (comparison)
Evaluated on held-out test set of 559,184 users

Layer 3 - Customer Segmentation
Break-even threshold · confidence tiers (High/Medium/Low)
Four-bucket classification with per-tier mean uplift

Layer 4 - Budget Optimizer
Greedy ROI allocation · High tier first (15.6x ROI)
Natural saturation point detection · DND exclusion value

Layer 5 - LLM Advisor
Groq Qwen 3.6-27B · JSON-grounded input
Mechanical hallucination verification pass

Layer 6 - Cloud Deployment
Model outputs to AWS S3 · Streamlit dashboard on AWS EC2
Training separated from serving

---

## Model Comparison — Why Transformed Outcome Won

Three approaches were tested and compared:

### T-Learner
Trains two separate XGBoost models — one on treatment users, one on control — then subtracts predictions to get per-user uplift.

**Result**: Qini 0.406. Underperformed because the 5.7x treatment/control imbalance (85%/15%) meant the control model trained on only 335K rows vs. 1.9M for treatment — producing noisier predictions and degraded uplift estimates.

### X-Learner with Propensity Weighting
Designed for imbalanced experiments — adds a propensity score weighting step to balance the two models.

**Result**: Qini 0.718, but calibration error of 10.6 percentage points (predicted 11.7% uplift when true uplift was 1.03%). Root cause: treatment was randomly assigned, so propensity scores clustered at 0.85 with no variation. The weighting step became meaningless. Unsuitable for threshold-based budget decisions despite high ranking quality.

### Transformed Outcome (Selected)
Mathematically transforms each observed outcome into an unbiased individual treatment effect estimate using the formula: tau = (T - g) / (g x (1-g)) x Y. Trains a single XGBoost regressor on all 2.2M training rows simultaneously.

**Result**: Qini 0.726, calibration error 0.000065. Best on both ranking quality and absolute accuracy. Specifically designed for randomized controlled trials where treatment probability g is known and constant.

---

## Key Analytical Decisions

**Why treatment not exposure as the causal variable**
Exposed users showed 41.4% visit rates vs. 3.8% for control — a 37.6pp gap. But this is selection bias: users whose browsers rendered the ad were already more engaged. Using treatment (intent-to-treat, randomly assigned) gives the honest 1.03pp average treatment effect.

**Why visit not conversion as the KPI**
Conversion rate was only 0.3% in the treatment group — too rare for reliable individual-level estimates. Visit rate (4.85%) provided sufficient statistical signal.

**Why the LLM narrative is grounded not free-form**
The LLM receives only a structured JSON summary of verified model outputs — never raw data. A post-generation verification pass checks every numeric claim against the source JSON. Hallucination risk confirmed LOW.

**Why the budget ceiling matters**
At $736.67 (test set scale), all 73,667 Persuadables have been reached. Any additional spend targets Sure Things or Lost Causes — zero incremental conversions. Scaled to the full 13.9M dataset, the implied optimal campaign budget is approximately $18,400.

---

## Technology Stack

| Layer | Tools |
|---|---|
| Data processing | Python, pandas, scikit-learn (stratified sampling) |
| Uplift modeling | XGBoost, scikit-uplift, custom Transformed Outcome |
| Evaluation | Qini coefficient, calibration error, SMD check |
| Segmentation | Custom break-even threshold, confidence tier logic |
| Budget optimizer | Greedy ROI allocation, saturation detection |
| LLM advisor | Groq API, Qwen 3.6-27B, JSON grounding, hallucination verification |
| Cloud storage | AWS S3, boto3 |
| Dashboard | Streamlit, Pillow |
| Deployment | AWS EC2 t3.micro |
| Version control | GitHub, Google Colab Pro (training) |

---

## Project Structure
Causal-Uplift-Budget-Optimizer/
├── streamlit_app.py              # Five-page Streamlit dashboard
├── src/
│   ├── segmentation.py           # Four-bucket classification + confidence tiers
│   ├── budget_optimizer.py       # Greedy ROI allocation + DND exclusion value
│   └── llm_advisor.py            # Groq LLM + hallucination verification
├── outputs/
│   ├── eda/                      # Randomization check + EDA charts
│   ├── model_results/            # Qini curves + model comparison
│   ├── segments/                 # Segment assignments + budget allocation
│   └── recommendations/          # LLM narrative + verification report
├── data/                         # Criteo dataset (downloaded via HuggingFace)
├── requirements.txt
└── README.md

---

## Limitations and Future Work

**Simulated cost assumptions**: cost per impression ($0.01) and revenue per conversion ($1.00) are placeholder values — a real deployment would use actual CPM and average order value.

**Static model**: batch-trained, not continuously updated. A production system would include drift detection (PSI-based score distribution monitoring) to trigger retraining when user behavior shifts.

**Criteo-specific features**: the 12 anonymized features (f0-f11) would be replaced with interpretable business features (recency, purchase history, category affinity) in a real deployment.

---

## Author

**Lakshmi Bharathy Kumar**
M.S. Applied Data Intelligence · San Jose State University · May 2026
[LinkedIn](https://linkedin.com/in/lakshmi-bharathy-kumar) · [GitHub](https://github.com/Lakshmibharathy11) · [Portfolio](https://lakshmibharathy11.github.io)

*Seeking entry-level roles in AI Engineering, Data Science, and Analytics in the Bay Area. Authorized to work in the U.S. without sponsorship.*
