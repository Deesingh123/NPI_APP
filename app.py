import streamlit as st
import importlib
import os

st.set_page_config(page_title="NPI Dashboard", layout="wide", initial_sidebar_state="expanded")

# Clean & Professional Design
st.markdown("""
<style>
    .main-header {
        font-size: 4.2rem;
        font-weight: 800;
        color: #1e40af;
        text-align: center;
        margin: 80px 0 30px 0;
    }
    .sub-header {
        font-size: 1.6rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 60px;
    }
    .footer-text {
        text-align: center;
        color: #9ca3af;
        font-size: 1rem;
        margin-top: 150px;
    }
    /* Sidebar styling */
    .css-1d391kg {  /* Sidebar background */
        background-color: #f8fafc;
    }
    .sidebar .sidebar-content {
        padding-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚀 NPI DASHBOARD</h1>', unsafe_allow_html=True)

# Get models
model_folders = [f for f in os.listdir("models") if os.path.isdir(os.path.join("models", f))]
model_names = [folder.replace("_", " ").upper() for folder in model_folders]

if not model_folders:
    st.error("No models found in 'models/' folder.")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.title("📊 Navigation")

    # Model selection
    selected_model = st.selectbox(
        "Select Model",
        options=model_folders,
        format_func=lambda x: x.replace("_", " ").upper(),
        index=0,
        key="selected_model"
    )

    # Dashboard selection
    selected_dashboard = st.radio(
        "Choose Dashboard",
        options=["readiness", "milestone"],
        format_func=lambda x: "📋 Process Readiness Tracker" if x == "readiness" else "🎯 Milestone Tracker Dashboard",
        key="selected_dashboard"
    )

    st.markdown("---")
    st.caption("Live data from Google Sheets")

# Main content - show selected dashboard
model_display = selected_model.replace("_", " ").upper()

#st.markdown(f'<h2 style="text-align:center; font-size:3rem; color:#1e40af; margin:60px 0 40px 0;">{model_display}</h2>', unsafe_allow_html=True)

file_path = f"models.{selected_model}.{selected_dashboard}"

try:
    module = importlib.import_module(file_path)
    module.main()
except Exception as e:
    st.error(f"Error loading {selected_dashboard} for {model_display}: {e}")
    st.info("Check folder and file names (case-sensitive).")

# Footer
st.markdown("""
<div class="footer-text">
    Live data from Google Sheets • Auto-refresh enabled • Mobile & desktop friendly
</div>
""", unsafe_allow_html=True)