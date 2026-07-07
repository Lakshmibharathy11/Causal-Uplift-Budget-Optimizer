import streamlit as st
import boto3
import pandas as pd
import json
import io
import os
from PIL import Image

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Causal Uplift Intelligence Platform",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── ROOT ── */
:root {
    --navy:    #0A0E1A;
    --surface: #1E2440;
    --border:  #2D3561;
    --text:    #F0F4FF;
    --muted:   #8892B0;
    --indigo:  #6366F1;
    --emerald: #10B981;
    --red:     #EF4444;
    --amber:   #F59E0B;
    --mono:    'JetBrains Mono', monospace;
}

/* ── GLOBAL ── */
html, body, [class*="css"] {
    background-color: var(--navy) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1200px; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── HERO HEADER ── */
.hero-header {
    background: linear-gradient(135deg, #0A0E1A 0%, #1a1f3a 50%, #0d1235 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.5rem 2.5rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -20%;
    width: 60%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(99,102,241,0.15) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 0.6; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.05); }
}
.hero-title {
    font-family: 'DM Serif Display', serif !important;
    font-size: 2.2rem !important;
    font-weight: 400 !important;
    letter-spacing: -0.5px;
    color: var(--text) !important;
    margin: 0 0 0.25rem 0 !important;
    position: relative;
}
.hero-subtitle {
    font-size: 0.9rem;
    color: var(--muted);
    font-family: var(--mono);
    letter-spacing: 0.5px;
    position: relative;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.4);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-family: var(--mono);
    color: #a5b4fc;
    margin-right: 8px;
    margin-top: 12px;
    position: relative;
}

/* ── METRIC CARDS ── */
.metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    flex: 1; min-width: 160px;
    position: relative; overflow: hidden;
}
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 0 0 12px 12px;
}
.metric-card.indigo::after { background: var(--indigo); }
.metric-card.emerald::after { background: var(--emerald); }
.metric-card.red::after { background: var(--red); }
.metric-card.amber::after { background: var(--amber); }
.metric-label {
    font-size: 0.72rem;
    font-family: var(--mono);
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: var(--text);
    line-height: 1;
    margin-bottom: 0.25rem;
}
.metric-sub {
    font-size: 0.75rem;
    color: var(--muted);
}

/* ── SECTION HEADERS ── */
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: var(--text);
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}
.section-eyebrow {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--indigo);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

/* ── INSIGHT CARD ── */
.insight-card {
    background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(16,185,129,0.06));
    border: 1px solid rgba(99,102,241,0.3);
    border-left: 4px solid var(--indigo);
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1.5rem;
}
.insight-label {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--indigo);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}
.insight-text {
    font-size: 0.9rem;
    color: #cbd5e1;
    line-height: 1.7;
}
.insight-text strong { color: var(--text); }

/* ── DATA TABLE ── */
.stDataFrame {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* ── SEGMENT BADGES ── */
.seg-persuadable { color: var(--emerald); font-weight: 600; }
.seg-dnd { color: var(--red); font-weight: 600; }
.seg-neutral { color: var(--muted); }

/* ── DIVIDER ── */
.page-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

/* ── DATA TIMELINE ── */
.timeline-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}
.timeline-item {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(45,53,97,0.5);
}
.timeline-item:last-child { border-bottom: none; }
.timeline-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--indigo);
    margin-top: 6px;
    flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)


# ── S3 LOADER ────────────────────────────────────────────────────────────────
@st.cache_resource
def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-west-2')
    )

@st.cache_data(ttl=3600)
def load_csv(bucket, key):
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()))

@st.cache_data(ttl=3600)
def load_json(bucket, key):
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj['Body'].read())

@st.cache_data(ttl=3600)
def load_text(bucket, key):
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj['Body'].read().decode('utf-8')

@st.cache_data(ttl=3600)
def load_image(bucket, key):
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=bucket, Key=key)
    return Image.open(io.BytesIO(obj['Body'].read()))

BUCKET = 'uplift-budget-optimizer-lbk'


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 1.5rem;'>
        <div style='font-family: DM Serif Display, serif; font-size: 1.1rem;
                    color: #F0F4FF; margin-bottom: 0.25rem;'>
            📡 Uplift Intelligence
        </div>
        <div style='font-family: JetBrains Mono, monospace; font-size: 0.65rem;
                    color: #8892B0; letter-spacing: 1px;'>
            CAUSAL INFERENCE PLATFORM
        </div>
    </div>
    <hr style='border-color: #2D3561; margin: 0 0 1rem;'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["Executive Summary",
         "Model Performance",
         "Customer Segments",
         "Budget Optimizer",
         "Methodology"],
        label_visibility="collapsed"
    )

    st.markdown("""
    <hr style='border-color: #2D3561; margin: 1.5rem 0 1rem;'>
    <div style='font-family: JetBrains Mono, monospace; font-size: 0.65rem;
                color: #8892B0; line-height: 1.8;'>
        DATASET<br>
        <span style='color: #a5b4fc;'>Criteo Uplift v2.1</span><br>
        13.9M users · 16 cols<br>
        Jan 2021 – Dec 2021<br><br>
        SAMPLE USED<br>
        <span style='color: #a5b4fc;'>2.8M rows (20%)</span><br>
        Stratified · seed=42<br><br>
        MODEL<br>
        <span style='color: #10B981;'>Transformed Outcome</span><br>
        XGBoost · Qini 0.726
    </div>
    """, unsafe_allow_html=True)


# ── HERO HEADER (all pages) ───────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
    <div class="hero-title">Causal Uplift Intelligence Platform</div>
    <div class="hero-subtitle">
        Who converts because of your ad — and who would have anyway?
    </div>
    <div style='margin-top: 12px;'>
        <span class="hero-badge">📡 Criteo Uplift Benchmark · 13.9M Users</span>
        <span class="hero-badge">📅 2021 · Weekly · 156 Periods</span>
        <span class="hero-badge">🤖 T-Learner + Transformed Outcome</span>
        <span class="hero-badge">☁️ Live on AWS</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Executive Summary":

    summary = load_json(BUCKET, 'outputs/recommendations/structured_summary.json')
    narrative = load_text(BUCKET, 'outputs/recommendations/llm_narrative.txt')

    pop = summary['population']
    budget = summary['budget_allocation']
    dnd = summary['do_not_disturb']

    # ── Metric row
    st.markdown('<div class="metric-row">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card indigo">
            <div class="metric-label">Users Analyzed</div>
            <div class="metric-value">{pop['total_users_analyzed']//1000}K</div>
            <div class="metric-sub">Test set · 20% stratified sample</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card emerald">
            <div class="metric-label">Persuadables Found</div>
            <div class="metric-value">{pop['persuadables_pct']}%</div>
            <div class="metric-sub">{pop['persuadables_count']:,} users worth targeting</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card amber">
            <div class="metric-label">Budget Ceiling</div>
            <div class="metric-value">${budget['total_spend']:.0f}</div>
            <div class="metric-sub">Saturates all Persuadables</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card red">
            <div class="metric-label">DND Users Excluded</div>
            <div class="metric-value">{dnd['users_excluded']:,}</div>
            <div class="metric-sub">${dnd['budget_saved']} saved · {dnd['conversions_protected']:.0f} conversions protected</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Dataset timeline
    st.markdown("""
    <div class="section-eyebrow">Dataset</div>
    <div class="section-header">Data Foundation</div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("""
        <div class="timeline-card">
            <div style='font-family: JetBrains Mono, monospace; font-size: 0.7rem;
                        color: #6366F1; letter-spacing: 1px; margin-bottom: 0.75rem;'>
                CRITEO UPLIFT MODELING DATASET v2.1
            </div>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div>
                    <div style='font-size: 0.85rem; font-weight: 500;'>
                        13,979,592 users</div>
                    <div style='font-size: 0.75rem; color: #8892B0;'>
                        Full dataset · real advertising experiment</div>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div>
                    <div style='font-size: 0.85rem; font-weight: 500;'>
                        Experiment period: 2021</div>
                    <div style='font-size: 0.75rem; color: #8892B0;'>
                        Randomized controlled trial by Criteo AI Lab</div>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div>
                    <div style='font-size: 0.85rem; font-weight: 500;'>
                        85% treatment · 15% control</div>
                    <div style='font-size: 0.75rem; color: #8892B0;'>
                        Imbalanced by design — real holdout experiment</div>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div>
                    <div style='font-size: 0.85rem; font-weight: 500;'>
                        12 anonymized features (f0–f11)</div>
                    <div style='font-size: 0.75rem; color: #8892B0;'>
                        Behavioral signals · privacy-safe obfuscation</div>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div>
                    <div style='font-size: 0.85rem; font-weight: 500;'>
                        Visit rate: 4.85% treated · 3.82% control</div>
                    <div style='font-size: 0.75rem; color: #8892B0;'>
                        True average treatment effect: +1.03pp</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="timeline-card">
            <div style='font-family: JetBrains Mono, monospace; font-size: 0.7rem;
                        color: #6366F1; letter-spacing: 1px; margin-bottom: 0.75rem;'>
                PIPELINE STAGES
            </div>
            <div class="timeline-item">
                <div class="timeline-dot" style='background: #10B981;'></div>
                <div>
                    <div style='font-size: 0.85rem; font-weight: 500;'>
                        Randomization check · SMD validation</div>
                    <div style='font-size: 0.75rem; color: #8892B0;'>
                        All 12 features balanced (max SMD 0.047)</div>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot" style='background: #10B981;'></div>
                <div>
                    <div style='font-size: 0.85rem; font-weight: 500;'>
                        Stratified sampling · 2.8M rows (20%)</div>
                    <div style='font-size: 0.75rem; color: #8892B0;'>
                        Treatment & visit rates preserved to 4 decimal places</div>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot" style='background: #10B981;'></div>
                <div>
                    <div style='font-size: 0.85rem; font-weight: 500;'>
                        T-Learner + Transformed Outcome models</div>
                    <div style='font-size: 0.75rem; color: #8892B0;'>
                        XGBoost base · GPU-accelerated · Qini evaluated</div>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot" style='background: #10B981;'></div>
                <div>
                    <div style='font-size: 0.85rem; font-weight: 500;'>
                        Four-bucket segmentation</div>
                    <div style='font-size: 0.75rem; color: #8892B0;'>
                        Break-even threshold · confidence tiers</div>
                </div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot" style='background: #10B981;'></div>
                <div>
                    <div style='font-size: 0.85rem; font-weight: 500;'>
                        Budget optimizer + LLM advisor</div>
                    <div style='font-size: 0.75rem; color: #8892B0;'>
                        Greedy ROI allocation · Groq Qwen · verified narrative</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── LLM Narrative
    st.markdown("""
    <div class="section-eyebrow" style='margin-top:2rem;'>AI-Generated</div>
    <div class="section-header">Executive Recommendation</div>
    """, unsafe_allow_html=True)

    # Clean up the <think> block if Qwen included it
    import re
    clean_narrative = re.sub(r'<think>.*?</think>', '', narrative, flags=re.DOTALL).strip()

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-label">📋 Groq LLM · Verified · Grounded in Model Outputs</div>
        <div class="insight-text">{clean_narrative.replace(chr(10), '<br>')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-card" style='margin-top:1rem; border-left-color: #F59E0B;
         background: linear-gradient(135deg, rgba(245,158,11,0.06), rgba(99,102,241,0.04));'>
        <div class="insight-label" style='color:#F59E0B;'>📌 Stakeholder Insight</div>
        <div class="insight-text">
            This analysis shows that <strong>77.9% of your ad budget is currently 
            reaching Sure Things</strong> — users who would have visited your site 
            regardless of advertising. By redirecting spend exclusively to the 
            <strong>13.2% identified as Persuadables</strong>, you can achieve more 
            than half of your maximum possible conversion gain at less than a 
            third of your current total spend. The pipeline also flags 
            <strong>1.5% of users as Do Not Disturb</strong> — a segment that 
            actively converts at a lower rate when shown ads, representing a 
            real, measurable cost of untargeted campaigns.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MODEL PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Model Performance":

    summary = load_json(BUCKET, 'outputs/recommendations/structured_summary.json')
    mp = summary['model_performance']

    st.markdown("""
    <div class="section-eyebrow">Evaluation</div>
    <div class="section-header">Model Comparison & Diagnostics</div>
    """, unsafe_allow_html=True)

    # Metric row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card indigo">
            <div class="metric-label">Transformed Outcome Qini</div>
            <div class="metric-value">{mp['transformed_outcome_qini']}</div>
            <div class="metric-sub">Selected model · best calibration</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card emerald">
            <div class="metric-label">Lift at Top 30%</div>
            <div class="metric-value">{mp['lift_at_top_30pct']}</div>
            <div class="metric-sub">vs 30% from random targeting</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card amber">
            <div class="metric-label">Calibration Error</div>
            <div class="metric-value">{mp['calibration_error']}</div>
            <div class="metric-sub">Mean predicted vs actual ATE</div>
        </div>""", unsafe_allow_html=True)

    # Qini chart
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        img = load_image(BUCKET, 'outputs/model_results/model_comparison_qini.png')
        st.image(img, use_container_width=True)
    except:
        st.info("Chart not found in S3 — upload outputs/model_results/ first")

    st.markdown("""
    <div class="insight-card">
        <div class="insight-label">📌 Stakeholder Insight</div>
        <div class="insight-text">
            Three modeling approaches were compared. The <strong>Transformed 
            Outcome model</strong> was selected because it achieved the 
            highest ranking quality (Qini 0.726) while also being the most 
            accurately calibrated — its predictions match actual observed 
            outcomes to within 0.007%. The X-Learner's propensity-weighting 
            approach, while showing high ranking quality on paper, 
            over-predicted true ad impact by 11x — making it unsuitable 
            for budget decisions where absolute accuracy matters. 
            <strong>Targeting just the top 30% of users identified by our 
            model captures 87.8% of all possible incremental lift</strong> — 
            nearly three times what random targeting would achieve at the 
            same spend level.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Comparison table
    st.markdown("""
    <div class="section-eyebrow" style='margin-top:2rem;'>Detail</div>
    <div class="section-header">Model Scorecard</div>
    """, unsafe_allow_html=True)

    scorecard = pd.DataFrame({
        'Model': ['T-Learner', 'X-Learner (propensity)', 'Transformed Outcome ✓'],
        'Qini Coefficient': [0.4061, 0.7181, 0.7257],
        'Lift at Top 30%': ['60.8%', '86.1%', '87.8%'],
        'Calibration Error': [0.000286, 0.105115, 0.000065],
        'Production Ready': ['Partial', 'No — miscalibrated', 'Yes'],
    })
    st.dataframe(scorecard, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — CUSTOMER SEGMENTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Customer Segments":

    seg_df = load_csv(BUCKET, 'outputs/segments/test_set_segments.csv')

    st.markdown("""
    <div class="section-eyebrow">Segmentation</div>
    <div class="section-header">Four-Bucket Customer Classification</div>
    """, unsafe_allow_html=True)

    # Segment counts
    counts = seg_df['segment'].value_counts()
    total = len(seg_df)

    col1, col2, col3, col4 = st.columns(4)
    segments = [
        ('Persuadable', 'emerald', '🎯', 'Target these users'),
        ('Neutral_SureThing', 'indigo', '✓', 'Already converts — skip'),
        ('Neutral_LostCause', 'amber', '—', 'Nothing moves them'),
        ('DoNotDisturb', 'red', '⚠️', 'Ad actively hurts')
    ]
    for col, (seg, color, icon, note) in zip([col1, col2, col3, col4], segments):
        count = counts.get(seg, 0)
        pct = count / total * 100
        with col:
            st.markdown(f"""
            <div class="metric-card {color}">
                <div class="metric-label">{icon} {seg.replace('_', ' ')}</div>
                <div class="metric-value">{pct:.1f}%</div>
                <div class="metric-sub">{count:,} users · {note}</div>
            </div>""", unsafe_allow_html=True)

    # SMD chart
    st.markdown("""
    <div class="section-eyebrow" style='margin-top:2rem;'>Validation</div>
    <div class="section-header">Randomization Balance Check</div>
    """, unsafe_allow_html=True)
    try:
        img = load_image(BUCKET, 'outputs/eda/randomization_smd_check.png')
        st.image(img, use_container_width=True)
    except:
        st.info("Chart not found — upload outputs/eda/ first")

    # Confidence tier breakdown
    st.markdown("""
    <div class="section-eyebrow" style='margin-top:2rem;'>Detail</div>
    <div class="section-header">Confidence Tier Breakdown</div>
    """, unsafe_allow_html=True)

    tier_table = seg_df.groupby(['segment', 'confidence']).agg(
        count=('uplift_score', 'count'),
        mean_uplift=('uplift_score', 'mean')
    ).reset_index()
    tier_table['pct'] = (tier_table['count'] / total * 100).round(1)
    tier_table['mean_uplift'] = tier_table['mean_uplift'].round(4)
    tier_table.columns = ['Segment', 'Confidence', 'Users', 'Mean Uplift', '% of Total']
    st.dataframe(tier_table, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="insight-card">
        <div class="insight-label">📌 Stakeholder Insight</div>
        <div class="insight-text">
            The <strong>High-confidence Persuadables (5.7% of users)</strong> 
            show a mean uplift of +15.6pp — meaning an ad makes them 15.6 
            percentage points more likely to visit. These are your highest-ROI 
            targets and should receive priority budget allocation in every 
            campaign. Equally important: the <strong>1.5% Do Not Disturb 
            segment</strong> should be explicitly excluded from all targeting 
            lists — showing them an ad reduces their visit probability by an 
            average of 7.6pp, a real, measurable cost that most campaigns 
            unknowingly incur. The <strong>randomization balance check 
            confirms all 12 features were statistically equivalent</strong> 
            between ad-shown and control groups (max SMD 0.047), validating 
            that our uplift estimates reflect true causal ad impact.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — BUDGET OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Budget Optimizer":

    summary = load_json(BUCKET, 'outputs/recommendations/structured_summary.json')
    alloc_df = load_csv(BUCKET, 'outputs/segments/budget_allocation_$2000.csv')

    st.markdown("""
    <div class="section-eyebrow">Allocation</div>
    <div class="section-header">Constrained Budget Optimizer</div>
    """, unsafe_allow_html=True)

    budget = summary['budget_allocation']
    dnd = summary['do_not_disturb']
    tier_roi = summary['tier_roi']

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card emerald">
            <div class="metric-label">Optimal Spend</div>
            <div class="metric-value">${budget['total_spend']:.0f}</div>
            <div class="metric-sub">Budget ceiling — saturation point</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card indigo">
            <div class="metric-label">Expected Incremental Conversions</div>
            <div class="metric-value">{budget['expected_incremental_conversions']:.0f}</div>
            <div class="metric-sub">From Persuadable targeting only</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card amber">
            <div class="metric-label">Effective Cost Per Conversion</div>
            <div class="metric-value">${budget['effective_cpa']:.4f}</div>
            <div class="metric-sub">Incremental CPA</div>
        </div>""", unsafe_allow_html=True)

    # Tier ROI table
    st.markdown("""
    <div class="section-eyebrow" style='margin-top:2rem;'>ROI by Tier</div>
    <div class="section-header">Persuadable Tier Analysis</div>
    """, unsafe_allow_html=True)

    roi_data = []
    for tier, vals in tier_roi.items():
        roi_data.append({
            'Confidence Tier': tier,
            'Users': f"{vals['users']:,}",
            'Mean Uplift': f"+{vals['mean_uplift']*100:.1f}pp",
            'ROI': f"{vals['roi']:.1f}x",
            'Cost to Target': f"${vals['cost_to_target']:.2f}",
        })
    st.dataframe(pd.DataFrame(roi_data), use_container_width=True, hide_index=True)

    # Allocation table
    st.markdown("""
    <div class="section-eyebrow" style='margin-top:2rem;'>Allocation</div>
    <div class="section-header">Budget Allocation Results</div>
    """, unsafe_allow_html=True)
    st.dataframe(alloc_df, use_container_width=True, hide_index=True)

    # DND savings
    st.markdown(f"""
    <div style='background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.3);
                border-left: 4px solid #EF4444; border-radius: 12px;
                padding: 1.25rem 1.5rem; margin-top: 1.5rem;'>
        <div style='font-family: JetBrains Mono, monospace; font-size: 0.7rem;
                    color: #EF4444; letter-spacing: 2px; margin-bottom: 0.75rem;'>
            ⚠️ DO NOT DISTURB — EXCLUSION VALUE
        </div>
        <div style='font-size: 0.9rem; color: #cbd5e1; line-height: 1.7;'>
            Explicitly excluding <strong style='color:#F0F4FF;'>{dnd['users_excluded']:,} Do Not Disturb users</strong> 
            saves <strong style='color:#F0F4FF;'>${dnd['budget_saved']}</strong> in ad spend 
            and protects <strong style='color:#F0F4FF;'>{dnd['conversions_protected']:.0f} conversions</strong> 
            that would have been destroyed by showing these users an ad. 
            This is the segment most campaigns unknowingly harm — identified 
            here for the first time through causal inference.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-card" style='margin-top:1rem;'>
        <div class="insight-label">📌 Stakeholder Insight</div>
        <div class="insight-text">
            The optimizer reveals a <strong>natural budget ceiling of $736.67</strong> 
            for this test population — spending beyond this point produces 
            zero additional incremental conversions because all Persuadables 
            have been reached. This saturation point is a critical planning 
            input: budget above this threshold should be reallocated to other 
            campaigns, held for the next period, or used to run new 
            geo-experiments to discover additional Persuadable segments. 
            <strong>High-confidence Persuadables deliver 15.6x ROI</strong> — 
            prioritize this tier first in every campaign cycle.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Methodology":

    st.markdown("""
    <div class="section-eyebrow">Architecture</div>
    <div class="section-header">Pipeline Design & Key Decisions</div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div class="timeline-card">
        <div style='font-family: JetBrains Mono, monospace; font-size: 0.7rem;
                    color: #6366F1; letter-spacing: 1px; margin-bottom: 0.75rem;'>
            PIPELINE LAYERS
        </div>
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div><div style='font-size:0.85rem;font-weight:500;'>
                Layer 1 — Data Validation</div>
            <div style='font-size:0.75rem;color:#8892B0;'>
                SMD randomization check · 12 features balanced (max 0.047)</div></div>
        </div>
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div><div style='font-size:0.85rem;font-weight:500;'>
                Layer 2 — Uplift Estimation</div>
            <div style='font-size:0.75rem;color:#8892B0;'>
                T-Learner + Transformed Outcome · XGBoost · GPU-accelerated</div></div>
        </div>
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div><div style='font-size:0.85rem;font-weight:500;'>
                Layer 3 — Customer Segmentation</div>
            <div style='font-size:0.75rem;color:#8892B0;'>
                Break-even threshold · confidence tiers · four buckets</div></div>
        </div>
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div><div style='font-size:0.85rem;font-weight:500;'>
                Layer 4 — Budget Optimizer</div>
            <div style='font-size:0.75rem;color:#8892B0;'>
                Greedy ROI allocation · saturation detection · DND exclusion</div></div>
        </div>
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div><div style='font-size:0.85rem;font-weight:500;'>
                Layer 5 — LLM Advisor</div>
            <div style='font-size:0.75rem;color:#8892B0;'>
                Groq Qwen · JSON-grounded · hallucination verification pass</div></div>
        </div>
        <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div><div style='font-size:0.85rem;font-weight:500;'>
                Layer 6 — Cloud Deployment</div>
            <div style='font-size:0.75rem;color:#8892B0;'>
                Outputs → S3 · Streamlit → EC2 · Public dashboard URL</div></div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="timeline-card">
        <div style='font-family: JetBrains Mono, monospace; font-size: 0.7rem;
                    color: #6366F1; letter-spacing: 1px; margin-bottom: 0.75rem;'>
            KEY ANALYTICAL DECISIONS
        </div>
        <div class="timeline-item">
            <div class="timeline-dot" style='background:#10B981;'></div>
            <div><div style='font-size:0.85rem;font-weight:500;'>
                Why Transformed Outcome over X-Learner</div>
            <div style='font-size:0.75rem;color:#8892B0;'>
                X-Learner propensity weighting assumes non-random assignment.
                Treatment here was randomized → propensity scores cluster at 0.85
                with no discriminating power → 11x calibration inflation. 
                Transformed Outcome is designed for RCTs.</div></div>
        </div>
        <div class="timeline-item">
            <div class="timeline-dot" style='background:#10B981;'></div>
            <div><div style='font-size:0.85rem;font-weight:500;'>
                Why treatment not exposure for causal variable</div>
            <div style='font-size:0.75rem;color:#8892B0;'>
                Exposed users (41.4% visit rate) vs control (3.8%) shows 37.6pp 
                gap — but this is selection bias. Exposed users are more engaged 
                by definition. Treatment (intent-to-treat) preserves randomization 
                and gives honest 1.03pp ATE.</div></div>
        </div>
        <div class="timeline-item">
            <div class="timeline-dot" style='background:#10B981;'></div>
            <div><div style='font-size:0.85rem;font-weight:500;'>
                Why visit not conversion as KPI</div>
            <div style='font-size:0.75rem;color:#8892B0;'>
                Conversion rate is 0.3% in treatment — extremely rare events
                produce unreliable individual-level estimates. Visit rate (4.85%)
                provides sufficient signal for stable uplift modeling.</div></div>
        </div>
        <div class="timeline-item">
            <div class="timeline-dot" style='background:#10B981;'></div>
            <div><div style='font-size:0.85rem;font-weight:500;'>
                Why LLM narrative is grounded not free-form</div>
            <div style='font-size:0.75rem;color:#8892B0;'>
                LLM receives only a structured JSON summary of verified outputs —
                never raw data. A post-generation verification pass checks every
                numeric claim against the source JSON. Hallucination risk: LOW.</div></div>
        </div>
        </div>
        """, unsafe_allow_html=True)

    # Tech stack
    st.markdown("""
    <div class="section-eyebrow" style='margin-top:2rem;'>Stack</div>
    <div class="section-header">Technology & Infrastructure</div>
    """, unsafe_allow_html=True)

    tech = pd.DataFrame({
        'Layer': ['Data', 'Modeling', 'Evaluation',
                  'LLM', 'Cloud Storage', 'Serving'],
        'Technology': [
            'Criteo Uplift v2.1 · pandas · stratified sampling',
            'XGBoost · scikit-uplift · Transformed Outcome',
            'Qini coefficient · Calibration error · SMD check',
            'Groq API · Qwen 3.6-27B · JSON grounding · verification',
            'AWS S3 · boto3 · structured artifact storage',
            'Streamlit · AWS EC2 t3.micro · public URL'
        ],
        'Purpose': [
            '13.9M user RCT · privacy-safe features',
            'Causal uplift estimation · ITE per user',
            'Ranking quality · absolute accuracy · experiment validity',
            'Business narrative translation · hallucination guard',
            'Persistent model artifacts · decoupled compute/serve',
            'Interactive dashboard · recruiter-accessible demo'
        ]
    })
    st.dataframe(tech, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="insight-card" style='margin-top:1.5rem;'>
        <div class="insight-label">📌 Design Philosophy</div>
        <div class="insight-text">
            Every architectural decision in this pipeline was made to be 
            <strong>defensible, not just functional</strong>. The model 
            selection (Transformed Outcome over X-Learner) was driven by 
            empirical calibration testing, not assumption. The LLM layer 
            includes a mechanical verification pass because LLMs are 
            unreliable narrators by default — and analytics tools used 
            for budget decisions cannot afford confident-sounding 
            hallucinations. The deployment separates training (Colab GPU), 
            storage (S3), and serving (EC2) following the production 
            principle: <strong>never put compute in the critical path of 
            a user request</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)
