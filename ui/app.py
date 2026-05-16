import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Production Config: Try to get URL from Streamlit Secrets, fallback to localhost
BASE_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="TrialMatch AI | Enterprise Pre-screening",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("TrialMatch AI")
st.sidebar.markdown("---")
nav = st.sidebar.radio("Navigation", ["Dashboard", "Patient Management", "Screening Engine", "Analytics"])

def fetch_patients():
    try:
        resp = requests.get(f"{BASE_URL}/patients")
        if resp.status_code == 200:
            return resp.json()
    except:
        return []
    return []

def fetch_reports():
    try:
        resp = requests.get(f"{BASE_URL}/reports")
        if resp.status_code == 200:
            return resp.json()
    except:
        return []
    return []

if nav == "Dashboard":
    st.title("🏥 Enterprise Clinical Trial Dashboard")
    
    reports = fetch_reports()
    patients = fetch_patients()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patients", len(patients))
    col2.metric("Total Screenings", len(reports))
    
    matches = [r for r in reports if r["eligibility_status"] == "match"]
    col3.metric("Eligible Matches", len(matches))
    col4.metric("Enrollment Rate", f"{round(len(matches)/len(reports)*100, 1) if reports else 0}%")

    st.markdown("---")
    
    if reports:
        df_r = pd.DataFrame(reports)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Eligibility Distribution")
            fig = px.pie(df_r, names='eligibility_status', hole=.4, 
                         color_discrete_sequence=['#2ecc71', '#e74c3c'])
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.subheader("Screening Latency (sec)")
            fig = px.histogram(df_r, x="processing_time_sec", nbins=20,
                               color_discrete_sequence=['#3498db'])
            st.plotly_chart(fig, use_container_width=True)

elif nav == "Patient Management":
    st.title("👥 Patient Records Management")
    
    with st.expander("➕ Generate Synthetic Cohort", expanded=False):
        count = st.number_input("Number of patients to generate", 1, 100, 10)
        if st.button("Generate & Persist"):
            with st.spinner("Executing Synthea simulation..."):
                resp = requests.post(f"{BASE_URL}/patients/generate?count={count}")
                if resp.status_code == 200:
                    st.success(f"Successfully integrated {count} new patient records.")
                    st.rerun()

    patients = fetch_patients()
    if patients:
        df_p = pd.DataFrame(patients)
        st.subheader("Recent Patient Records")
        st.dataframe(df_p, use_container_width=True)
    else:
        st.info("No patient records found. Generate a cohort to begin.")

elif nav == "Screening Engine":
    st.title("🤖 AI Screening Engine")
    st.info("Current Trial: **ONCO-2025-001 - Phase II Ovarian Cancer PARP Inhibitor Study**")
    
    patients = fetch_patients()
    reports = fetch_reports()
    screened_ids = [r["patient_id"] for r in reports]
    unscreened = [p for p in patients if p["id"] not in screened_ids]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Engine Controls")
        if st.button("🚀 Run Batch Screening", type="primary", disabled=not unscreened):
            with st.spinner("LangGraph Agent Orchestration in progress..."):
                resp = requests.post(f"{BASE_URL}/screen/batch")
                if resp.status_code == 200:
                    st.success("Batch screening complete!")
                    st.rerun()
        
        st.write(f"Pending Patients: **{len(unscreened)}**")
        
    with col2:
        st.subheader("Live Screening Log")
        if reports:
            for r in reports[:10]:
                status = "✅" if r["eligibility_status"] == "match" else "❌"
                st.write(f"{status} **Patient {r['patient_id'][:8]}**: {r['eligibility_status'].upper()} - {r['reasoning'][:100]}...")
        else:
            st.write("No screening logs available.")

elif nav == "Analytics":
    st.title("📊 Clinical Site Analytics")
    reports = fetch_reports()
    
    if reports:
        df_r = pd.DataFrame(reports)
        matched = df_r[df_r["eligibility_status"] == "match"].copy()
        
        if not matched.empty:
            # Extract site name from the full report JSON if needed, or use ID
            st.subheader("Site Allocation Capacity")
            # For simplicity in demo, we'll just count by site ID
            site_counts = matched["assigned_site_id"].value_counts().reset_index()
            site_counts.columns = ["Site ID", "Allocated Patients"]
            
            fig = px.bar(site_counts, x="Site ID", y="Allocated Patients", 
                         title="Matched Patients per Trial Site",
                         color="Allocated Patients",
                         color_continuous_scale="Viridis")
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Detailed Match Matrix")
            st.table(matched[["patient_id", "assigned_site_id", "processing_time_sec"]])
        else:
            st.info("No eligible matches found to analyze.")
    else:
        st.info("Run screening to generate analytics data.")

st.sidebar.markdown("---")
st.sidebar.info(f"Last sync: {datetime.now().strftime('%H:%M:%S')}")
