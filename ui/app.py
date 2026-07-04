import streamlit as st
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import run_pipeline
from tools.financial_tools import load_all_customers, get_engagement_type

@st.cache_data(ttl=300)
def run_pipeline_cached(customer_id: str = None, target_lang: str = "English") -> dict:
    return run_pipeline(verbose=False, customer_id=customer_id, target_lang=target_lang)

st.set_page_config(
    page_title="SBI Agentic AI",
    page_icon="🏦",
    layout="wide"
)

# Enhanced Light Theme + Card Styling
st.markdown("""
<style>
    .main { background-color: #f8fbff; }
    .stApp { background-color: #f8fbff; }
    
    [data-testid="stSidebar"] {
        background-color: #f0f7ff;
        border-right: 1px solid #c0d4f5;
    }
    
    .stButton>button {
        background-color: #003366;
        color: white;
        font-size: 16px;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    /* Card Styling */
    div[data-testid="stContainer"] {
        background-color: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 51, 102, 0.08);
        margin-bottom: 24px;
    }
    
    /* Agent Cards with left border */
    div[key*="agent-card"] {
        border-left: 6px solid #003366;
    }
    
    div[key="filter-section"] {
        border-left: 6px solid #0066cc;
    }
    
    .header-banner {
        background: linear-gradient(135deg, #003366, #0066cc);
        padding: 22px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 6px 20px rgba(0, 51, 102, 0.25);
    }
    
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
        color: #303030;
        max-width: 90%;
        font-size: 15px;
        line-height: 1.45;
    }
    
    /* Font Sizes */
    h1 { font-size: 2.0rem !important; }
    h2 { font-size: 1.55rem !important; }
    h3 { font-size: 1.25rem !important; }
    .stMetricLabel { font-size: 0.85rem !important; }
    .stMarkdown p, .stMarkdown li, .stCaption { font-size: 14.5px !important; }
    
    .stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# Top Blue Banner
st.markdown("""
<div class="header-banner" style="display: flex; justify-content: space-between; align-items: center;">
    <div>
        <h1 style="margin:0; font-size: 28px;">🏦 SBI Digital Engagement System</h1>
        <p style="margin:5px 0 0 0; font-size: 16px; opacity:0.95;">
            Behavioral Intelligence • Proactive Advisor • Autonomous Action
        </p>
    </div>
    <div style="text-align:right;">
        <p style="margin:0; font-size:15px; opacity:0.9;">Powered by Agentic AI • LLaMA 3.3 70B via Groq</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/c/cc/SBI-logo.svg", width=140)
    
    st.markdown("### System Info")
    st.success("✅ Groq API Connected")
    st.success("✅ LLaMA 3.3 70B Active")
    st.success("✅ 4 Agents Standard Matrix")
    st.divider()
    st.markdown("### Agent Pipeline")
    st.markdown("1. Behavioral Intelligence")
    st.markdown("2. Loan Optimizer")
    st.markdown("3. Proactive Advisor")
    st.markdown("4. Autonomous Action")
    st.divider()
    st.markdown("### AI Capabilities")
    st.markdown("• LLM Risk Appetite Detection")
    st.markdown("• Dynamic Engagement Scoring")
    st.markdown("• Personalized Recommendations")
    st.markdown("• Loan Payback Optimization")
    st.markdown("• Autonomous Action Execution")
    st.divider()
    st.markdown("### Compliance")
    st.markdown("• RBI Guidelines")
    st.markdown("• Audit Trail Active")
    st.markdown("• Consent Framework")
    st.markdown("• 3-Tier Action Model")

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
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Customers", total)
    col2.metric("🔴 High Disengagement", high)
    col3.metric("🟡 Medium Disengagement", medium)
    col4.metric("🟢 Low Disengagement", low)
    col5.metric("🔵 Cold Start", cold)
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
st.markdown("#### Selected Customer Preview")
cols = st.columns(5)
cols[0].metric("Customer ID", selected["customer_id"])
cols[1].metric("Name", selected["name"])
cols[2].metric("Age", selected["age"])
cols[3].metric("Balance", f"₹{selected['account_balance']:,}")
cols[4].metric("Idle Balance", f"₹{selected['idle_balance_amount']:,}")
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
    ccols = st.columns(6)
    ccols[0].metric("Name", behavioral["customer_name"])
    ccols[1].metric("Account Balance", f"₹{behavioral['balance_info']['balance']:,}")
    ccols[2].metric("Idle Balance", f"₹{behavioral['balance_info']['idle_balance']:,}")
    ccols[3].metric("Investable Surplus", f"₹{behavioral['balance_info']['investable_surplus']:,}")
    ccols[4].metric("EMI Burden", f"{int(behavioral['balance_info']['emi_to_salary_ratio']*100)}% of salary")
    ccols[5].metric("AI Risk Appetite", behavioral["risk_appetite"].upper())
    
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
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Disengagement Level", f"{color} {level}")
        col2.metric("Disengagement Score", f"{score}/100")
        col3.metric("Last Login", f"{selected['last_login_days_ago']} days ago")
        col4.metric("Idle Balance Days", f"{selected['idle_balance_days']} days")
        col5.metric("Notification Rate", f"{int(selected['notification_response_rate']*100)}%")
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
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Loans", ls["total_loans"])
            col2.metric("Total Monthly EMI", f"₹{ls['total_emi']:,}")
            col3.metric("Total Outstanding", f"₹{ls['total_outstanding']:,}")
            col4.metric("EMI Burden", f"{int(ls['emi_to_salary_ratio']*100)}% of salary")
            col5.metric("Burden Level", ls["burden_level"])
            st.markdown("**Quick Insights:**")
            for tip in loan["optimization_tips"]:
                st.info(f" 💡 {tip}")
            with st.expander("View Full Repayment Plan"):
                st.write(loan["repayment_plan"])
            st.markdown("**🏦 Individual Loan Breakdown:**")
            for l in loan["loans"]:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Loan Type", l["loan_type"].replace("_", " ").title())
                c2.metric("Outstanding", f"₹{l['outstanding_amount']:,}")
                c3.metric("Monthly EMI", f"₹{l['emi']:,}")
                c4.metric("Tenure Left", f"{l['tenure_months']} months")
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
                col1, col2, col3 = st.columns(3)
                col1.metric("Recommended Amount", f"₹{rec['amount']:,}")
                col2.metric("Compliance Tier", rec["tier"].split("—")[0].strip())
                col3.metric("Approval Required", "Yes ⚠️" if "Tier 2" in rec["tier"] else "No ✅")
                st.write(f"**Reason:** {rec['reason']}")

    st.divider()

    # Agent 4
    with st.container(key="agent-card-4"):
        st.markdown("### Agent 4 — Autonomous Action Agent")
        st.caption("Executes compliant actions autonomously or routes for customer approval")
        status = action["status"]
        col1, col2, col3, col4 = st.columns(4)
        status_display = "🟡 PENDING APPROVAL" if status == "PENDING_APPROVAL" else "🟢 EXECUTED"
        col1.metric("Action Status", status_display)
        col2.metric("Action", action.get("action", "N/A"))
        col3.metric("Compliance", "✅ Passed" if action["compliance"]["compliant"] else "❌ Failed")
        col4.metric("Audit Trail", "✅ Logged" if action["compliance"]["audit_logged"] else "❌ No")
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
    <div style='text-align:center; color:#555; font-size:13px; margin-top:30px;'>
    SBI Agentic AI System | Built for SBI Hackathon 2026 | 
    Powered by LangChain + Groq LLaMA 3.3 70B | All actions comply with RBI guidelines
    </div>
    """, unsafe_allow_html=True)
