import streamlit as st

if 'selected_page' not in st.session_state:
    st.error("No model selected.")
    st.stop()

filename = st.session_state.selected_page
model_name = filename.split("_", 1)[1].replace(".py", "").replace("_", " ").upper()

st.markdown(f'<h1 style="text-align:center; font-size:4.5rem; color:#1e40af;">{model_name}</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; font-size:1.6rem; color:#64748b; margin-bottom:100px;">Select a dashboard</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("📋 Process Readiness Tracker", key="readiness", use_container_width=True, type="primary"):
        st.switch_page(f"pages/{filename}")

with col2:
    if st.button("🎯 Milestone Tracker Dashboard", key="milestone", use_container_width=True, type="primary"):
        st.switch_page(f"pages/2_Milestone_Tracker.py")  # or make separate per model

if st.button("← Back"):
    del st.session_state.selected_page
    st.switch_page("app.py")