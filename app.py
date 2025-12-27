import streamlit as st
import importlib
import os

st.set_page_config(page_title="NPI Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for buttons
st.markdown("""
<style>
    .main-header { 
        font-size: 4.2rem; font-weight: 800; color: #1e40af; text-align: center; margin: 60px 0 20px 0; 
    }
    .dashboard-btn {
        height: 70px !important;
        font-size: 1.2rem !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        margin: 10px 5px !important;
    }
    .footer-text { 
        text-align: center; color: #9ca3af; font-size: 1rem; margin-top: 100px; 
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<h1 class="main-header">🚀 NPI DASHBOARD</h1>', unsafe_allow_html=True)

# Get models
model_folders = [f for f in os.listdir("models") if os.path.isdir(os.path.join("models", f))]

if not model_folders:
    st.error("No models found in 'models/' folder.")
    st.stop()

# === SIDEBAR: Only Model Selection ===
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

# Model name display
#model_display = selected_model.replace("_", " ").upper()
#st.markdown(f"<h2 style='text-align:center; color:#1e40af; font-size:2.8rem; font-weight:700; margin:40px 0 30px 0;'>{model_display}</h2>", unsafe_allow_html=True)

# === HORIZONTAL DASHBOARD BUTTONS AT TOP ===
st.markdown("<div style='text-align:center; margin:30px 0;'>", unsafe_allow_html=True)

btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)

with btn_col1:
    if st.button("📋 **Readiness**", use_container_width=True, key="btn_readiness", help="Process Readiness Tracker"):
        st.session_state.selected_dashboard = "readiness"

with btn_col2:
    if st.button("🎯 **Milestone**", use_container_width=True, key="btn_milestone", help="Milestone Tracker Dashboard"):
        st.session_state.selected_dashboard = "milestone"

with btn_col3:
    if st.button("📈 **Plan**", use_container_width=True, key="btn_plan", help="Project Plan"):
        st.session_state.selected_dashboard = "plan"

with btn_col4:
    if st.button("📊 **KPI**", use_container_width=True, key="btn_kpi", help="KPI Dashboard"):
        st.session_state.selected_dashboard = "kpi"

with btn_col5:
    if st.button("📝 **MOM**", use_container_width=True, key="btn_mom", help="Minutes of Meeting"):
        st.session_state.selected_dashboard = "mom"

st.markdown("</div>", unsafe_allow_html=True)

# Default dashboard
if "selected_dashboard" not in st.session_state:
    st.session_state.selected_dashboard = "readiness"

# Load selected dashboard
selected_dashboard = st.session_state.selected_dashboard
file_path = f"models.{selected_model}.{selected_dashboard}"

try:
    module = importlib.import_module(file_path)
    module.main()
except Exception as e:
    st.error(f"Error loading {selected_dashboard.upper()} for {model_display}: {e}")
    st.info("Check if the file exists: models/{selected_model}/{selected_dashboard}.py")

# Footer
st.markdown("""
<div class="footer-text">
    Live data from Google Sheets • Auto-refresh enabled • Mobile & desktop friendly
</div>
""", unsafe_allow_html=True)
