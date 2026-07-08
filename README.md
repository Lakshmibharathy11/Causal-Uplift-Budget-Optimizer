
---

## Model Comparison — Why Transformed Outcome Won

Three approaches were tested and compared:

### T-Learner
Trains two separate XGBoost models — one on treatment users, one on control — then subtracts predictions to get per-user uplift.

**Result**: Qini 0.406. Underperformed because the 5.7x treatment/control imbalance (85%/15%) meant the control model trained on only 335K rows vs. 1.9M for treatment — producing noisier predictions and degraded uplift estimates.

### X-Learner with Propensity Weighting
Designed for imbalanced experiments — adds a propensity score weighting step to balance the two models' contributions.

**Result**: Qini 0.718, but **calibration error of 10.6 percentage points** (predicted 11.7% uplift when true uplift was 1.03% — a 10x overestimate). Root cause: treatment was randomly assigned, so propensity scores clustered at exactly 0.85 with no variation (std = 0.007). The weighting step became meaningless, putting 85% weight on the noisier control model. **Unsuitable for threshold-based budget decisions despite high ranking quality.**

### Transformed Outcome ✓ (Selected)
Mathematically transforms each user's observed outcome into an unbiased individual treatment effect estimate using the formula: `τ = (T - g) / (g × (1-g)) × Y`. Trains a single XGBoost regressor on all 2.2M training rows simultaneously — no split, no imbalance problem.

**Result**: Qini 0.726, calibration error 0.000065. Best on both ranking quality and absolute accuracy. Specifically designed for randomized controlled trials where treatment probability g is known and constant — exactly the Criteo experimental setup.

---

## Key Analytical Decisions

**Why `treatment` not `exposure` as the causal variable**
Exposed users (those who actually saw the ad render) showed 41.4% visit rates vs. 3.8% for control — a 37.6pp gap. But this is selection bias: users whose browsers rendered the ad were already more engaged. Using `treatment` (intent-to-treat, randomly assigned) gives the honest 1.03pp average treatment effect.

**Why `visit` not `conversion` as the KPI**
Conversion rate was only 0.3% in the treatment group — too rare to estimate reliable individual-level effects. Visit rate (4.85%) provided sufficient statistical signal for stable uplift modeling.

**Why the LLM narrative is grounded not free-form**
The LLM receives only a structured JSON summary of verified model outputs — never raw data. A post-generation verification pass checks every numeric claim in the narrative against the source JSON. Hallucination risk confirmed LOW across all runs.

**Why the budget ceiling matters**
At $736.67 (test set scale), all 73,667 Persuadables have been reached. Any additional spend targets Sure Things or Lost Causes — zero incremental conversions. Scaled to the full 13.9M dataset, the implied optimal campaign budget is approximately $18,400.

---

## Technology Stack

| Layer | Tools |
|---|---|
| Data processing | Python · pandas · scikit-learn (stratified sampling) |
| Uplift modeling | XGBoost · scikit-uplift · custom Transformed Outcome implementation |
| Evaluation | Qini coefficient · calibration error · SMD randomization check |
| Segmentation | Custom break-even threshold · confidence tier logic |
| Budget optimizer | Greedy ROI allocation · saturation detection |
| LLM advisor | Groq API · Qwen 3.6-27B · JSON grounding · hallucination verification |
| Cloud storage | AWS S3 · boto3 |
| Dashboard | Streamlit · Pillow |
| Deployment | AWS EC2 t3.micro · screen session management |
| Version control | GitHub · Google Colab Pro (training) |

---

## Project Structure
---
├── streamlit_app.py              
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
---

## Limitations & Future Work

**Simulated cost assumptions**: cost per impression ($0.01) and revenue per conversion ($1.00) are placeholder values — a real deployment would use actual CPM from the ad platform and actual average order value from the business.

**National-level analysis only**: the pipeline models all users as one population. A geo-level or segment-level analysis would reveal whether uplift patterns differ across user groups.

**Static model**: the pipeline is batch-trained, not continuously updated. A production system would include drift detection (PSI-based score distribution monitoring) to trigger retraining when user behavior patterns shift.

**Criteo-specific features**: the 12 anonymized features (f0–f11) are specific to Criteo's internal representation. A real deployment would replace these with interpretable business features (recency, purchase history, category affinity) and add SHAP-based feature importance analysis.

---

## Author

**Lakshmi Bharathy Kumar**  
M.S. Applied Data Intelligence · San Jose State University · May 2026  
[LinkedIn](https://linkedin.com/in/lakshmi-bharathy-kumar) · [GitHub](https://github.com/Lakshmibharathy11) · [Portfolio](https://lakshmibharathy11.github.io)

*Seeking entry-level roles in AI Engineering, Data Science, and Analytics in the Bay Area. Authorized to work in the U.S. without sponsorship.*
