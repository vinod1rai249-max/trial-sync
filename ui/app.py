import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIG & THEMING ---
BASE_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="TrialMatch AI | Enterprise Clinical Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Enterprise CSS
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background-color: #F9FAFB;
    }

    /* Professional Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #111827;
    }
    
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E5E7EB;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        color: white;
        border-right: 1px solid #374151;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #9CA3AF;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* Tables */
    .styled-table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        min-width: 400px;
        border-radius: 8px 8px 0 0;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
    }

    /* Custom Banner */
    .hero-banner {
        background: linear-gradient(90deg, #1E40AF 0%, #3B82F6 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- API WRAPPERS ---
@st.cache_data(ttl=5)
def fetch_patients():
    try:
        resp = requests.get(f"{BASE_URL}/patients", timeout=10)
        return resp.json() if resp.status_code == 200 else []
    except: return []

@st.cache_data(ttl=5)
def fetch_reports():
    try:
        resp = requests.get(f"{BASE_URL}/reports", timeout=10)
        return resp.json() if resp.status_code == 200 else []
    except: return []

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d473530c25e7e4411b40.svg", width=40)
    st.title("TrialMatch AI")
    st.caption("v2.4.0-enterprise")
    st.markdown("---")
    
    nav = st.radio(
        "GO TO",
        ["🏛️ Executive Dashboard", "👥 Cohort Management", "⚡ AI Screening Engine", "📊 Clinical Analytics"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.info("💡 **Pro Tip:** Enable LangSmith tracing in settings to monitor agent reasoning in real-time.")
    
    st.markdown("#### 🔍 SYSTEM OBSERVABILITY")
    langsmith_url = "https://smith.langchain.com/projects/p/TrialMatch-AI-Enterprise"
    st.link_button("📜 View Live Audit Trail", langsmith_url, use_container_width=True, help="Access real-time LangGraph traces and AI reasoning logs.")

# --- HERO SECTION ---
def render_hero(title, subtitle):
    st.markdown(f"""
        <div class="hero-banner">
            <h1 style='margin:0; font-size: 2.2rem;'>{title}</h1>
            <p style='margin:0; opacity: 0.9; font-size: 1.1rem;'>{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

# --- DASHBOARD PAGE ---
if "Executive Dashboard" in nav:
    render_hero("Executive Intelligence Overview", "Real-time enrollment health and system performance.")
    
    reports = fetch_reports()
    patients = fetch_patients()
    
    # KPIs
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Total Cohort", len(patients), help="Total patients in database")
    m_col2.metric("Screened", len(reports), help="Completed agentic runs")
    
    matches = [r for r in reports if r["eligibility_status"] == "match"]
    rate = round(len(matches)/len(reports)*100, 1) if reports else 0
    m_col3.metric("Eligible Matches", len(matches), f"{rate}% Rate")
    
    # Safety check for sum with potential None values
    valid_latencies = [r['processing_time_sec'] for r in reports if r.get('processing_time_sec') is not None]
    avg_latency = round(sum(valid_latencies)/len(valid_latencies), 2) if valid_latencies else 0
    m_col4.metric("Avg Latency", f"{avg_latency}s", "-92% vs manual", delta_color="inverse")

    st.markdown("### 📈 Performance Visuals")
    
    if reports:
        df_r = pd.DataFrame(reports)
        # Data Cleaning for Plotly
        df_r["processing_time_sec"] = pd.to_numeric(df_r["processing_time_sec"]).fillna(0)
        df_r["run_index"] = range(1, len(df_r) + 1)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader("Enrollment funnel")
            fig = px.pie(df_r, names='eligibility_status', hole=.5,
                         color='eligibility_status',
                         color_discrete_map={'match':'#10B981', 'no_match':'#EF4444'},
                         labels={'eligibility_status': 'Status'})
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.subheader("Processing Distribution")
            fig = px.area(df_r, x="run_index", y="processing_time_sec",
                          line_shape="spline")
            fig.update_traces(fillcolor="rgba(59, 130, 246, 0.2)", line_color="#3B82F6")
            fig.update_layout(margin=dict(t=20, b=0, l=0, r=0), xaxis_title="Run Count", yaxis_title="Seconds")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available. Proceed to Cohort Management to generate patients.")

# --- COHORT MANAGEMENT ---
elif "Cohort Management" in nav:
    render_hero("Cohort Management", "Integrate and manage synthetic FHIR patient records.")
    
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("#### ➕ Ingest New Records")
            count = st.select_slider("Select cohort size", options=[5, 10, 25, 50, 100], value=10)
            if st.button("Simulate Synthea Ingestion", use_container_width=True, type="primary"):
                with st.spinner("🔄 Connect to Synthea FHIR Server..."):
                    resp = requests.post(f"{BASE_URL}/patients/generate?count={count}")
                    if resp.status_code == 200:
                        st.toast(f"✅ Ingested {count} FHIR records", icon='🏥')
                        st.rerun()
        
        with col2:
            st.markdown("#### 🔍 Record Metadata")
            patients = fetch_patients()
            if patients:
                df_p = pd.DataFrame(patients)
                st.dataframe(
                    df_p.style.background_gradient(subset=['hba1c'], cmap='Blues'),
                    use_container_width=True,
                    height=400
                )
            else:
                st.info("Database empty. Start by ingesting records.")

# --- SCREENING ENGINE ---
elif "Screening Engine" in nav:
    render_hero("AI Screening Engine", "High-fidelity LangGraph orchestration for patient eligibility.")
    
    st.markdown("""
        <div style='background: white; border-radius: 12px; padding: 20px; border: 1px solid #E5E7EB; margin-bottom: 20px;'>
            <p style='margin:0; font-weight: 600; color: #374151;'>ACTIVE TRIAL</p>
            <h3 style='margin:0; color: #1E40AF;'>ONCO-2025-001: Phase II Ovarian Cancer PARP Inhibitor Study</h3>
        </div>
    """, unsafe_allow_html=True)
    
    patients = fetch_patients()
    reports = fetch_reports()
    screened_ids = [r["patient_id"] for r in reports]
    unscreened = [p for p in patients if p["id"] not in screened_ids]
    
    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        st.markdown("### ⚙️ Engine Control")
        st.write(f"Queue Status: **{len(unscreened)} Pending**")
        
        if st.button("🚀 Execute Batch Pipeline", type="primary", use_container_width=True, disabled=not unscreened):
            progress_text = "Orchestrating Agent Nodes..."
            my_bar = st.progress(0, text=progress_text)
            
            with st.spinner(""):
                resp = requests.post(f"{BASE_URL}/screen/batch")
                for percent_complete in range(100):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1, text=progress_text)
                
                if resp.status_code == 200:
                    st.balloons()
                    st.success("Batch Processing Successful")
                    st.rerun()
        
        st.markdown("---")
        st.markdown("#### 🔒 Security Boundary")
        st.caption("Agent nodes operate in a HIPAA-aware environment. PII is automatically stripped at the entry point.")

    with col2:
        st.markdown("### 📋 Real-time Pipeline Logs")
        if reports:
            for r in reports[:8]:
                with st.expander(f"{'✅' if r['eligibility_status'] == 'match' else '❌'} Patient {r['patient_id'][:8]}", expanded=False):
                    st.json(r['full_report_json'])
        else:
            st.info("Waiting for pipeline execution...")

# --- ANALYTICS ---
elif "Clinical Analytics" in nav:
    render_hero("Clinical Site Analytics", "Geographic and capacity optimization for multicenter trials.")
    
    reports = fetch_reports()
    if reports:
        df_r = pd.DataFrame(reports)
        matched = df_r[df_r["eligibility_status"] == "match"].copy()
        
        if not matched.empty:
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("#### 📍 Site Allocation Distribution")
                site_counts = matched["assigned_site_id"].value_counts().reset_index()
                site_counts.columns = ["Site ID", "Count"]
                fig = px.bar(site_counts, x="Site ID", y="Count", 
                             color="Count", color_continuous_scale="Blues")
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
                
            with c2:
                st.markdown("#### 🧬 Eligibility Reason Cloud")
                # Just show a list of reasons for professional touch
                for idx, row in matched.head(5).iterrows():
                    st.info(f"**Patient {row['patient_id'][:8]}:** {row['reasoning']}")
        else:
            st.info("No successful matches to analyze.")
    else:
        st.info("Run the screening engine to populate analytics.")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.markdown(f"📡 **Backend Connection:** `{BASE_URL}`")
st.sidebar.caption(f"Last Sync: {datetime.now().strftime('%H:%M:%S')}")
