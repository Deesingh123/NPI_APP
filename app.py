import streamlit as st
import importlib
import os

st.set_page_config(page_title="NPI Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 4.2rem; font-weight: 800; color: #1e40af; text-align: center; margin: 80px 0 30px 0; }
    .sub-header { font-size: 1.6rem; color: #64748b; text-align: center; margin-bottom: 60px; }
    .footer-text { text-align: center; color: #9ca3af; font-size: 1rem; margin-top: 150px; }
    .css-1d391kg { background-color: #f8fafc; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚀 NPI DASHBOARD</h1>', unsafe_allow_html=True)

# Get models
model_folders = [f for f in os.listdir("models") if os.path.isdir(os.path.join("models", f))]

if not model_folders:
    st.error("No models found in 'models/' folder.")
    st.stop()

# === SIDEBAR: ONLY Model Selection ===
with st.sidebar:
    st.title("📊 Navigation")

    selected_model = st.selectbox(
        "Select Model",
        options=model_folders,
        format_func=lambda x: x.replace("_", " ").upper(),
        key="model_select"
    )

    st.markdown("---")
    st.caption("Live data from Google Sheets")

# === DASHBOARD SELECTION AT TOP (Clean Buttons) ===
model_display = selected_model.replace("_", " ").upper()
#st.markdown(f'<h2 style="text-align:center; font-size:3rem; color:#1e40af; font-weight:bold; margin:60px 0 40px 0;">{model_display}</h2>', unsafe_allow_html=True)

# Dashboard buttons at top
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("📋 Readiness", use_container_width=True):
        selected_dashboard = "readiness"

with col2:
    if st.button("🎯 Milestone", use_container_width=True):
        selected_dashboard = "milestone"

with col3:
    if st.button("📈 Plan", use_container_width=True):
        selected_dashboard = "plan"

with col4:
    if st.button("📊 KPI", use_container_width=True):
        selected_dashboard = "kpi"

with col5:
    if st.button("📝 MOM", use_container_width=True):
        selected_dashboard = "mom"

# Default to readiness if none selected
if 'selected_dashboard' not in locals():
    selected_dashboard = "readiness"

# Load the selected dashboard
file_path = f"models.{selected_model}.{selected_dashboard}"

try:
    module = importlib.import_module(file_path)
    module.main()
except Exception as e:
    st.error(f"Error loading {selected_dashboard} for {model_display}: {e}")
    st.info("Available: readiness.py, milestone.py, plan.py, kpi.py, mom.py")

# Footer
st.markdown("""
<div class="footer-text">
    Live data from Google Sheets • Auto-refresh enabled • Mobile & desktop friendly
</div>
""", unsafe_allow_html=True)
