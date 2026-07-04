import streamlit as st
import sys
import os
import re
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import run_pipeline
from tools.financial_tools import load_all_customers, get_engagement_type

# Matches the emoji characters used across the dashboard (🔴🟡🟢🔵✅❌⚠️ etc.)
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\u2600-\u27BF"
    "\uFE0F"
    "]+"
)

def _shrink_emojis(text: str, size: str = "0.65em") -> str:
    """Wrap emoji characters in a smaller span, leaving normal text untouched."""
    return _EMOJI_PATTERN.sub(lambda m: f'<span style="font-size:{size};">{m.group(0)}</span>', str(text))

def stat_chip(label: str, value, accent: str = "#4a90e2"):
    """Render one labeled value as a small bordered, theme-aware card.
    Used everywhere a group of 'parameters' is shown (customer stats,
    agent outputs, etc.) instead of a plain, borderless st.metric()."""
    value_html = _shrink_emojis(value)
    st.markdown(f"""
    <div style="
        background: var(--background-color);
        border: 1px solid color-mix(in srgb, var(--text-color) 14%, transparent);
        border-top: 3px solid {accent};
        border-radius: 10px;
        padding: 10px 14px 12px 14px;
        min-height: 68px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
    ">
        <div style="font-size:0.66rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase;
                    color:color-mix(in srgb, var(--text-color) 55%, transparent); margin-bottom:4px;">{label}</div>
        <div style="font-size:1.05rem; font-weight:700; color:var(--text-color); line-height:1.25; word-break:break-word;">{value_html}</div>
    </div>
    """, unsafe_allow_html=True)

def stat_row(items, widths=None):
    """Render a row of stat_chip()s across equal (or weighted) columns.
    items: list of (label, value) or (label, value, accent_hex) tuples."""
    columns = st.columns(widths if widths else len(items))
    for col, item in zip(columns, items):
        label, value = item[0], item[1]
        accent = item[2] if len(item) > 2 else "#4a90e2"
        with col:
            stat_chip(label, value, accent)

@st.cache_data(ttl=300)
def run_pipeline_cached(customer_id: str = None, target_lang: str = "English") -> dict:
    return run_pipeline(verbose=False, customer_id=customer_id, target_lang=target_lang)

st.set_page_config(
    page_title="SBI Agentic AI",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Styling
st.markdown("""
<style>
    /* ══════════════════════════════════════════════════════════════
       Theme-aware colors: everything below reads from Streamlit's own
       theme variables (--background-color, --secondary-background-color,
       --text-color) instead of fixed hex values, so the whole page
       switches correctly whether the user is on Light or Dark mode
       (Settings ▸ Choose app theme). color-mix() is used to derive
       muted/tinted tones (borders, captions, dots) directly from the
       active text color so they always have the right contrast.
       ══════════════════════════════════════════════════════════════ */

    .main { background-color: var(--background-color); }
    .stApp { background-color: var(--background-color); }

    /* ── Sidebar – now with a clearly different background, thick border, and strong shadow ── */
    [data-testid="stSidebar"] {
        background-color: color-mix(in srgb, var(--background-color) 85%, var(--text-color)) !important;
        border-right: 3px solid color-mix(in srgb, var(--text-color) 40%, transparent) !important;
        box-shadow: 4px 0 20px color-mix(in srgb, var(--text-color) 20%, transparent) !important;
    }
    
    /* Ensure Streamlit's inner div doesn't override our custom color */
    [data-testid="stSidebar"] > div:first-child {
        background-color: transparent !important;
    }

    .stButton>button {
        background-color: #4a90e2;
        color: #ffffff;
        font-size: 16px;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #357abd;
        color: #ffffff;
    }

    /* Cards */
    div[class*="st-key-filter-section"],
    div[class*="st-key-agent-card"] {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid color-mix(in srgb, var(--text-color) 12%, transparent);
        box-shadow: 0 4px 20px color-mix(in srgb, var(--text-color) 10%, transparent);
        margin-bottom: 24px;
    }
    div[class*="st-key-agent-card"] { border-left: 6px solid #2f6fd1; }
    div[class*="st-key-filter-section"] { border-left: 6px solid #4a90e2; }

    /* Header banner keeps its own fixed navy gradient + white text in
       both themes — it's an opaque brand block, not part of the page
       background, so it doesn't need to flip with the theme. */
    .header-banner {
        background: linear-gradient(135deg, #003366, #0066cc);
        padding: 22px 30px;
        border-radius: 12px;
        color: #ffffff;
        margin-bottom: 25px;
    }
    .header-banner h1, .header-banner p { color: #ffffff !important; }

    /* WhatsApp simulator is a fixed light-chat mockup on purpose (that's
       what WhatsApp looks like) so its colors stay constant too. */
    .whatsapp-container {
        background-color: #e5ddd5;
        background-image: url('https://user-images.githubusercontent.com/15075759/28719144-86dc0f70-73b1-11e7-911d-60d70fcded21.png');
        padding: 24px;
        border-radius: 18px;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.12);
        margin: 20px 0;
    }
    .whatsapp-bubble {
        background-color: #dcf8c6;
        padding: 14px 18px;
        border-radius: 18px 18px 4px 18px;
        color: #263426;
        max-width: 90%;
        font-size: 15px;
        line-height: 1.45;
    }

    /* Fonts */
    h1 { font-size: 1.95rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.2rem !important; }
    .stMarkdown p, .stMarkdown li, .stCaption { font-size: 14px !important; }

    /* ── Metric fix: stop long values (Customer ID, Name, etc.) from
       being cut off with "…". Shrink the value font, allow it to wrap,
       and force the color to follow the active theme's text color. ── */
    [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        word-break: break-word !important;
        line-height: 1.25 !important;
        color: var(--text-color) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        white-space: normal !important;
        overflow: visible !important;
        color: color-mix(in srgb, var(--text-color) 65%, transparent) !important;
    }
    [data-testid="stMetric"] {
        overflow: visible !important;
    }

    /* ══════════════════ Sidebar redesign tokens ══════════════════ */
    [data-testid="stSidebar"] .block-container { padding-top: 1rem; }

    .sb-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 14px;
        margin-bottom: 14px;
        background: color-mix(in srgb, var(--text-color) 7%, transparent);
        border: 1px solid color-mix(in srgb, var(--text-color) 24%, transparent);
        border-radius: 12px;
        box-shadow: 0 2px 8px color-mix(in srgb, var(--text-color) 8%, transparent);
    }
    .sb-header img { flex-shrink: 0; }
    .sb-header-title {
        font-size: 13.5px;
        font-weight: 700;
        color: var(--text-color);
        line-height: 1.25;
    }
    .sb-header-sub {
        font-size: 10.5px;
        color: color-mix(in srgb, var(--text-color) 55%, transparent);
        margin-top: 1px;
    }

    .sb-card {
        background: color-mix(in srgb, var(--text-color) 7%, transparent);
        border: 1px solid color-mix(in srgb, var(--text-color) 24%, transparent);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px color-mix(in srgb, var(--text-color) 8%, transparent);
    }
    .sb-card:last-child { margin-bottom: 0; }

    .sb-label {
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        color: color-mix(in srgb, var(--text-color) 55%, transparent);
        margin-bottom: 9px;
    }

    /* System status — compact key/value rows, no colored pill backgrounds */
    .sb-status-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 0;
        font-size: 12.3px;
        color: var(--text-color);
    }
    .sb-status-row .sb-status-key { display: flex; align-items: center; gap: 7px; }
    .sb-status-row .sb-dot { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; flex-shrink: 0; }
    .sb-status-row .sb-status-val {
        font-weight: 600;
        color: color-mix(in srgb, #22c55e 65%, var(--text-color) 35%);
        font-size: 11.8px;
    }

    /* Agent pipeline — slim numbered list, order is real so numbering earns its place */
    .sb-step { position: relative; padding-left: 26px; padding-bottom: 11px; }
    .sb-step:last-child { padding-bottom: 0; }
    .sb-step:not(.sb-step-last)::after {
        content: '';
        position: absolute;
        left: 8px; top: 19px;
        width: 1px; height: calc(100% - 6px);
        background: color-mix(in srgb, var(--text-color) 18%, transparent);
    }
    .sb-step-circle {
        position: absolute; left: 0; top: 0.5px;
        width: 17px; height: 17px; border-radius: 50%;
        background: #4a90e2; color: #ffffff;
        font-size: 9.5px; font-weight: 700;
        display: flex; align-items: center; justify-content: center;
    }
    .sb-step-title { font-size: 12.3px; font-weight: 600; color: var(--text-color); line-height: 1.3; }
    .sb-step-desc { font-size: 10.8px; color: color-mix(in srgb, var(--text-color) 55%, transparent); margin-top: 0px; }

    /* Capability / compliance lists — plain, monochrome, minimal */
    .sb-list { list-style: none; margin: 0; padding: 0; }
    .sb-list li {
        display: flex; align-items: flex-start; gap: 7px;
        font-size: 12px; color: var(--text-color);
        padding: 3px 0;
    }
    .sb-list li::before {
        content: '';
        width: 4px; height: 4px; border-radius: 50%;
        background: color-mix(in srgb, var(--text-color) 40%, transparent);
        margin-top: 6px;
        flex-shrink: 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-banner" style="display: flex; justify-content: space-between; align-items: center;">
    <div>
        <h1 style="margin:0; font-size: 28px;">🏦 SBI Digital Engagement System</h1>
        <p style="margin:5px 0 0 0; font-size: 16px; opacity:0.95;">Behavioral Intelligence • Proactive Advisor • Autonomous Action</p>
    </div>
    <div style="text-align:right;">
        <p style="margin:0; font-size:15px; opacity:0.9;">Powered by Agentic AI • LLaMA 3.3 70B via Groq</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Compact header — logo + title inline instead of stacked and oversized
    st.markdown("""
    <div class="sb-header">
        <img src="https://upload.wikimedia.org/wikipedia/commons/c/cc/SBI-logo.svg" width="34">
        <div>
            <div class="sb-header-title">SBI Agentic Console</div>
            <div class="sb-header-sub">Digital Engagement System</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # System status — flat key/value rows, no pill backgrounds
    st.markdown("""
    <div class="sb-card">
        <div class="sb-label">System Status</div>
        <div class="sb-status-row">
            <span class="sb-status-key"><span class="sb-dot"></span>Groq API</span>
            <span class="sb-status-val">Connected</span>
        </div>
        <div class="sb-status-row">
            <span class="sb-status-key"><span class="sb-dot"></span>LLaMA 3.3 70B</span>
            <span class="sb-status-val">Active</span>
        </div>
        <div class="sb-status-row">
            <span class="sb-status-key"><span class="sb-dot"></span>Agent Matrix</span>
            <span class="sb-status-val">4 · Standard</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Agent pipeline — slim connected numbered list, tighter spacing
    st.markdown("""
    <div class="sb-card">
        <div class="sb-label">Agent Pipeline</div>
        <div class="sb-step">
            <div class="sb-step-circle">1</div>
            <div class="sb-step-title">Behavioral Intelligence</div>
            <div class="sb-step-desc">Reads engagement signals</div>
        </div>
        <div class="sb-step">
            <div class="sb-step-circle">2</div>
            <div class="sb-step-title">Loan Optimizer</div>
            <div class="sb-step-desc">Plans repayment strategy</div>
        </div>
        <div class="sb-step">
            <div class="sb-step-circle">3</div>
            <div class="sb-step-title">Proactive Advisor</div>
            <div class="sb-step-desc">Drafts personalized outreach</div>
        </div>
        <div class="sb-step sb-step-last">
            <div class="sb-step-circle">4</div>
            <div class="sb-step-title">Autonomous Action</div>
            <div class="sb-step-desc">Executes or routes for approval</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # AI capabilities — plain minimal list
    st.markdown("""
    <div class="sb-card">
        <div class="sb-label">AI Capabilities</div>
        <ul class="sb-list">
            <li>LLM risk appetite detection</li>
            <li>Dynamic engagement scoring</li>
            <li>Personalized recommendations</li>
            <li>Loan payback optimization</li>
            <li>Autonomous action execution</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Compliance — plain minimal list
    st.markdown("""
    <div class="sb-card">
        <div class="sb-label">Compliance</div>
        <ul class="sb-list">
            <li>RBI guidelines</li>
            <li>Audit trail active</li>
            <li>Consent framework</li>
            <li>3-tier action model</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# CUSTOMER SELECTOR
with st.container(key="filter-section"):
    st.markdown("### 🔎 Customer Selector")
    st.caption("Engagement types are **dynamically calculated by the AI** from raw customer signals — nothing is pre-labeled.")
    
    all_customers = load_all_customers()
    for c in all_customers:
        c["_engagement_type"] = get_engagement_type(c)
    
    total = len(all_customers)
    high = sum(1 for c in all_customers if c["_engagement_type"] == "High Disengagement")
    medium = sum(1 for c in all_customers if c["_engagement_type"] == "Medium Disengagement")
    low = sum(1 for c in all_customers if c["_engagement_type"] == "Low Disengagement")
    cold = sum(1 for c in all_customers if c["_engagement_type"] == "Cold Start")
    
    stat_row([
        ("Total Customers", total, "#4a90e2"),
        ("🔴 High Disengagement", high, "#ef4444"),
        ("🟡 Medium Disengagement", medium, "#eab308"),
        ("🟢 Low Disengagement", low, "#22c55e"),
        ("🔵 Cold Start", cold, "#3b82f6"),
    ])
    st.divider()
    
    colA, colB, colC = st.columns([1, 1, 1.4])
    with colA:
        engagement_options = ["All Customers", "🔴 High Disengagement", "🟡 Medium Disengagement", "🟢 Low Disengagement", "🔵 Cold Start"]
        selected_filter = st.selectbox("Filter by Engagement Type", engagement_options)
    with colB:
        chosen_language = st.selectbox("🌐 Notification Output Language", ["English", "Hindi", "Telugu", "Marathi", "Tamil", "Bengali"])
    
    filter_map = {
        "All Customers": None,
        "🔴 High Disengagement": "High Disengagement",
        "🟡 Medium Disengagement": "Medium Disengagement",
        "🟢 Low Disengagement": "Low Disengagement",
        "🔵 Cold Start": "Cold Start"
    }
    filter_value = filter_map[selected_filter]
    filtered_customers = all_customers if not filter_value else [c for c in all_customers if c["_engagement_type"] == filter_value]
    
    with colC:
        if not filtered_customers:
            st.warning("No customers match this filter.")
            st.stop()
        customer_options = {f"{c['customer_id']} — {c['name']} ({c['_engagement_type']})": c["customer_id"] for c in filtered_customers}
        selected_label = st.selectbox("Select Customer to Analyze", list(customer_options.keys()))
        selected_customer_id = customer_options[selected_label]
    
    st.markdown(f"**Showing {len(filtered_customers)} customer(s):**")
    
    table_data = []
    for c in filtered_customers:
        emoji = "🔴" if c["_engagement_type"] == "High Disengagement" else \
                "🟡" if c["_engagement_type"] == "Medium Disengagement" else \
                "🔵" if c["_engagement_type"] == "Cold Start" else "🟢"
        has_loans = "loans" in c and len(c.get("loans", [])) > 0
        table_data.append({
            "Customer ID": c["customer_id"],
            "Name": c["name"],
            "Age": c["age"],
            "City": c["city"],
            "Occupation": c["occupation"],
            "Balance": f"₹{c['account_balance']:,}",
            "Idle Balance": f"₹{c['idle_balance_amount']:,}",
            "Last Login": f"{c['last_login_days_ago']} days ago",
            "Has Loans": "Yes 🏦" if has_loans else "No",
            "AI Detected Engagement": f"{emoji} {c['_engagement_type']}"
        })
    
    st.dataframe(table_data, use_container_width=True, height=380)

# Selected Customer Preview
selected = next(c for c in all_customers if c["customer_id"] == selected_customer_id)
st.markdown("### Selected Customer Preview")
# Weighted columns: Customer ID and Name get more room since they hold longer text
stat_row([
    ("Customer ID", selected["customer_id"], "#4a90e2"),
    ("Name", selected["name"], "#4a90e2"),
    ("Age", selected["age"], "#4a90e2"),
    ("Balance", f"₹{selected['account_balance']:,.0f}", "#22c55e"),
    ("Idle Balance", f"₹{selected['idle_balance_amount']:,.0f}", "#eab308"),
], widths=[1.4, 1.5, 0.7, 1.1, 1.1])
st.divider()

# Run Pipeline Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run = st.button("🚀 Run Engagement Pipeline", type="primary", use_container_width=True)

if run:
    progress = st.progress(0, text="Initializing pipeline...")
    with st.spinner(""):
        progress.progress(10, text="Loading customer profile...")
        time.sleep(0.3)
        progress.progress(25, text="LLM calculating risk appetite...")
        result = run_pipeline_cached(customer_id=selected_customer_id, target_lang=chosen_language)
        progress.progress(60, text="Running Proactive Advisor Agent...")
        time.sleep(0.3)
        progress.progress(85, text="Running Autonomous Action Agent...")
        time.sleep(0.3)
        progress.progress(100, text="✅ Pipeline Complete!")
    
    behavioral = result["behavioral"]
    advisor = result["advisor"]
    action = result["action"]
    
    st.success(f"✅ Pipeline completed for **{behavioral['customer_name']}** ({selected_customer_id})")
    st.divider()

    # Customer Profile
    st.markdown("### Customer Profile")
    risk_label = behavioral["risk_appetite"].upper()
    risk_accent = {"LOW": "#22c55e", "MODERATE": "#eab308", "HIGH": "#ef4444"}.get(risk_label, "#4a90e2")
    stat_row([
        ("Name", behavioral["customer_name"], "#4a90e2"),
        ("Account Balance", f"₹{behavioral['balance_info']['balance']:,.0f}", "#4a90e2"),
        ("Idle Balance", f"₹{behavioral['balance_info']['idle_balance']:,.0f}", "#eab308"),
        ("Investable Surplus", f"₹{behavioral['balance_info']['investable_surplus']:,.0f}", "#22c55e"),
        ("EMI Burden", f"{int(behavioral['balance_info']['emi_to_salary_ratio']*100)}% of salary", "#3b82f6"),
        ("AI Risk Appetite", risk_label, risk_accent),
    ], widths=[1.2, 1.3, 1.1, 1.3, 1.1, 1.1])
    
    if behavioral['balance_info']['loan_count'] > 0:
        st.markdown(f"**🏦 Active Loans: {behavioral['balance_info']['loan_count']} loan(s) | Total Monthly EMI: ₹{behavioral['balance_info']['total_emi']:,} | Total Outstanding: ₹{behavioral['balance_info']['total_outstanding']:,}**")
    st.divider()

    # Agent 1
    with st.container(key="agent-card-1"):
        st.markdown("### Agent 1 — Behavioral Intelligence Agent")
        st.caption("Analyzes customer signals and calculates disengagement score dynamically")
        level = behavioral["disengagement"]["disengagement_level"]
        score = behavioral["disengagement"]["disengagement_score"]
        color = "🔴" if level == "High" else "🟡" if level == "Medium" else "🔵" if level == "Cold Start" else "🟢"
        level_accent = {"High": "#ef4444", "Medium": "#eab308", "Cold Start": "#3b82f6"}.get(level, "#22c55e")
        stat_row([
            ("Disengagement Level", f"{color} {level}", level_accent),
            ("Disengagement Score", f"{score}/100", "#4a90e2"),
            ("Last Login", f"{selected['last_login_days_ago']} days ago", "#4a90e2"),
            ("Idle Balance Days", f"{selected['idle_balance_days']} days", "#4a90e2"),
            ("Notification Rate", f"{int(selected['notification_response_rate']*100)}%", "#4a90e2"),
        ])
        st.markdown("**⚠️ Risk Signals Detected:**")
        if behavioral["disengagement"]["signals"]:
            for signal in behavioral["disengagement"]["signals"]:
                st.warning(f"⚠️ {signal}")
        else:
            st.success("✅ No disengagement signals detected")
        with st.expander("View Full Behavioral Analysis"):
            st.write(behavioral["analysis"])

    st.divider()

    # Agent 2
    loan = result["loan"]
    with st.container(key="agent-card-2"):
        st.markdown("### Agent 2 — Loan Optimizer Agent")
        st.caption("Plans optimal loan repayment strategy based on salary and outstanding debt")
        if loan["has_loans"]:
            ls = loan["loan_summary"]
            burden_accent = {"high": "#ef4444", "medium": "#eab308"}.get(str(ls["burden_level"]).lower(), "#22c55e")
            stat_row([
                ("Total Loans", ls["total_loans"], "#4a90e2"),
                ("Total Monthly EMI", f"₹{ls['total_emi']:,}", "#4a90e2"),
                ("Total Outstanding", f"₹{ls['total_outstanding']:,}", "#eab308"),
                ("EMI Burden", f"{int(ls['emi_to_salary_ratio']*100)}% of salary", "#3b82f6"),
                ("Burden Level", ls["burden_level"], burden_accent),
            ])
            st.markdown("**Quick Insights:**")
            for tip in loan["optimization_tips"]:
                st.info(f" 💡 {tip}")
            with st.expander("View Full Repayment Plan"):
                st.write(loan["repayment_plan"])
            st.markdown("**🏦 Individual Loan Breakdown:**")
            for l in loan["loans"]:
                stat_row([
                    ("Loan Type", l["loan_type"].replace("_", " ").title(), "#4a90e2"),
                    ("Outstanding", f"₹{l['outstanding_amount']:,}", "#eab308"),
                    ("Monthly EMI", f"₹{l['emi']:,}", "#4a90e2"),
                    ("Tenure Left", f"{l['tenure_months']} months", "#22c55e"),
                ])
        else:
            st.success(f"✅ {loan['message']}")

    # Agent 3
    with st.container(key="agent-card-3"):
        st.markdown("### Agent 3 — Proactive Advisor Agent")
        st.caption("Generates personalized recommendations matched to targeted banking strategies")
        st.markdown(f"**Dynamic Optimization Target:** `{advisor['best_recommendation']}`")
        st.markdown(f"**Target Language Generation Strategy:** `{advisor['target_language']}`")
        st.info(f"**Internal Log System View:**\n\n{advisor['personalized_message']}")
        
        st.markdown("#### 📱 Outbound Delivery Sandbox (Omni-channel WhatsApp Simulator)")
        st.caption("Simulated secure gateway callback layer processing edge notifications at zero operational cost.")
        
        st.markdown('<div class="whatsapp-container">', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="whatsapp-bubble">
                <strong>💬 Official SBI Assistant:</strong><br>
                {advisor['personalized_message']}
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"**All Backend Options Generated: {len(advisor['recommendations'])}**")
        for i, rec in enumerate(advisor["recommendations"]):
            badge = " Best Match" if i == 0 else f"Option {i+1}"
            with st.expander(f"{badge}: {rec['action']}"):
                needs_approval = "Tier 2" in rec["tier"]
                stat_row([
                    ("Recommended Amount", f"₹{rec['amount']:,}", "#22c55e"),
                    ("Compliance Tier", rec["tier"].split("—")[0].strip(), "#4a90e2"),
                    ("Approval Required", "Yes ⚠️" if needs_approval else "No ✅", "#eab308" if needs_approval else "#22c55e"),
                ])
                st.write(f"**Reason:** {rec['reason']}")

    st.divider()

    # Agent 4
    with st.container(key="agent-card-4"):
        st.markdown("### Agent 4 — Autonomous Action Agent")
        st.caption("Executes compliant actions autonomously or routes for customer approval")
        status = action["status"]
        status_display = "🟡 PENDING APPROVAL" if status == "PENDING_APPROVAL" else "🟢 EXECUTED"
        status_accent = "#eab308" if status == "PENDING_APPROVAL" else "#22c55e"
        compliant = action["compliance"]["compliant"]
        audit_logged = action["compliance"]["audit_logged"]
        stat_row([
            ("Action Status", status_display, status_accent),
            ("Action", action.get("action", "N/A"), "#4a90e2"),
            ("Compliance", "✅ Passed" if compliant else "❌ Failed", "#22c55e" if compliant else "#ef4444"),
            ("Audit Trail", "✅ Logged" if audit_logged else "❌ No", "#22c55e" if audit_logged else "#ef4444"),
        ])
        st.success(f"{action['status_update']}")
        with st.expander("View Full Audit Log"):
            if action["audit_log"]:
                st.json(action["audit_log"][0])

    st.divider()

    # Approval Section
    if status == "PENDING_APPROVAL":
        st.markdown("### Customer Approval Required")
        st.warning(f"**Action:** {action['action']} | **Amount:** ₹{action.get('amount', 0):,} | **Requires your explicit consent**")
        col1, col2 = st.columns(2)
        if col1.button("✅ Approve Action", type="primary", use_container_width=True):
            st.success("✅ Action approved! Transaction initiated and audit logged securely via SMS/WhatsApp framework simulation.")
            st.balloons()
        if col2.button("Reject Action", use_container_width=True):
            st.error("Action rejected by customer. No transaction executed. Rejection audit logged.")

    st.divider()
    st.markdown("""
    <div style='text-align:center; color:color-mix(in srgb, var(--text-color) 65%, transparent); font-size:13px; margin-top:30px;'>
    SBI Agentic AI System | Built for SBI Hackathon 2026 | 
    Powered by LangChain + Groq LLaMA 3.3 70B | All actions comply with RBI guidelines
    </div>
    """, unsafe_allow_html=True)
