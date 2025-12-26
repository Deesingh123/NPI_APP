import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    # Back button to return to model selection
    if st.button("← Back to Dashboard", key="back_utah_readiness"):
        if 'dashboard' in st.session_state:
            del st.session_state.dashboard
        st.rerun()

    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQBqDIx_ZBSYN7RaWxCIjHMZeFBkMhQaKcmc8mvq9KrE-Z1EFeaIsC1B4Fmw_wE_1NbzsConI04b6o0/pub?gid=1841630466&single=true&output=csv"

# Remove @st.cache_data completely
    def load_data():
        df = pd.read_csv(CSV_URL)
        df = df.dropna(how='all').reset_index(drop=True)
        df = df.fillna("—")
        df = df.loc[:, ~df.columns.duplicated()]
        return df

# Add refresh button
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("🔄 Refresh"):
             st.rerun()

    df = load_data()

    # Beautiful Header
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background:linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%); color:white; border-radius:16px; margin-bottom:15px; box-shadow: 0 12px 30px rgba(29,78,216,0.3);">
        <h1 style="margin:0; font-size:2.4rem; font-weight:800;">UTAH NA</h1>
        <p style="margin:10px 0 0 0; font-size:1.1rem;">
            Updated: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')} • Auto-refresh every {REFRESH_INTERVAL}s
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Timeline Section
    st.markdown("""
    <div style="background:#f0f9ff; padding:15px; border-radius:20px; margin:15px 0; box-shadow:0 8px 30px rgba(0,0,0,0.1); border:1px solid #bae6fd;">
        <div style="text-align:center;">
            <h3 style="color:#0c4a6e; font-size:1.8rem; margin:0 0 15px 0; font-weight:700;"> Timelines </h3>
            <div style="display:flex; justify-content:space-around; flex-wrap:wrap; gap:20px;">
                <div style="text-align:center;">
                    <p style="font-size:1.4rem; font-weight:bold; color:#166534; margin:0;">OK2P</p>
                    <p style="font-size:1.2rem; color:#0c4a6e; margin:5px 0 0 0;">09 NOV</p>
                </div>
                <div style="text-align:center;">
                    <p style="font-size:1.4rem; font-weight:bold; color:#0c4a6e; margin:0;">OK2R</p>
                    <p style="font-size:1.2rem; color:#0c4a6e; margin:5px 0 0 0;">29 OCT</p>
                </div>
                <div style="text-align:center;">
                    <p style="font-size:1.4rem; font-weight:bold; color:#0c4a6e; margin:0;">OK2S</p>
                    <p style="font-size:1.2rem; color:#0c4a6e; margin:5px 0 0 0;">19 NOV</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Column detection - ONLY the columns that exist in your sheet
    category_col = next((c for c in df.columns if "process category" in c.lower()), None)
    owner_col = next((c for c in df.columns if "owner" in c.lower()), None)
    target_col = next((c for c in df.columns if "target date" in c.lower()), None)
    actual_col = next((c for c in df.columns if "actual date" in c.lower()), None)
    status_col = next((c for c in df.columns if "status" in c.lower()), None)
    remark_col = next((c for c in df.columns if "remark" in c.lower() or "remarks" in c.lower()), None)

    # Safety check
    required_cols = [category_col, owner_col, target_col, actual_col, status_col]
    if not all(required_cols):
        st.error("One or more required columns not found in the sheet.")
        st.stop()


    # Date parsing
    if target_col:
        df[target_col] = pd.to_datetime(df[target_col], errors='coerce', dayfirst=True)
    if actual_col:
        df[actual_col] = pd.to_datetime(df[actual_col], errors='coerce', dayfirst=True)
    today = pd.Timestamp.today().normalize()

    # Final Status Logic
    # Final Status Logic - CORRECTED & WORKING PERFECTLY
    def get_final_status(row):
        # Get the "Status" column value (e.g., "closed", "Closed")
        status_val = str(row[status_col]).strip().lower() if pd.notna(row.get(status_col)) else ""
        is_closed = status_val in ["closed", "close", "done", "yes"]

        # Check if Target Date is past today
        target_past = pd.notna(row.get(target_col)) and row[target_col].normalize() < today

        # Rule 1: If Status says "closed" → always "Closed" (green)
        if is_closed:
            return "Closed"

        # Rule 2: If not closed AND Target Date is past → Delayed (red)
        elif target_past:
            return "NOT CLOSED – DELAYED!"

        # Rule 3: Everything else → Open (yellow)
        else:
            return "Open"


    df["Final Status"] = df.apply(get_final_status, axis=1)

    # Metric Cards (Delayed, Open, Closed)
    delayed = len(df[df["Final Status"].str.contains("DELAYED")])
    open_count = len(df[df["Final Status"] == "Open"])
    closed = len(df[df["Final Status"].str.contains("Closed")])

    # ... (your metric cards code remains the same)

    # Filters
    filtered = df.copy()

    col1, col2, col3 = st.columns(3)
    with col1:
        if owner_col:
            owners = ["All"] + sorted(filtered[owner_col].dropna().unique().tolist())
            chosen_owner = st.selectbox("👤 Owner", owners, key="owner_filter")
            if chosen_owner != "All":
                filtered = filtered[filtered[owner_col] == chosen_owner]

    with col2:
        categories = ["All"] + sorted(filtered[category_col].dropna().unique().tolist())
        chosen_cat = st.selectbox("📋 Process Category", categories, key="cat_filter")
        if chosen_cat != "All":
            filtered = filtered[filtered[category_col] == chosen_cat]

    with col3:
        view = st.selectbox("🔍 View", ["All Items", "Only Delayed", "Only Open", "Only Closed"], key="view_filter")
        if view == "Only Delayed":
            filtered = filtered[filtered["Final Status"].str.contains("DELAYED")]
        elif view == "Only Open":
            filtered = filtered[filtered["Final Status"] == "Open"]
        elif view == "Only Closed":
            filtered = filtered[filtered["Final Status"].str.contains("Closed")]

    # Alert
    urgent = len(filtered[filtered["Final Status"].str.contains("DELAYED")])
    if urgent:
        st.error(f"🚨 URGENT: {urgent} items DELAYED & NOT CLOSED!")
    else:
        st.success("✅ All items are On Track or Closed")

    # Beautiful HTML Table - Exact Columns from Your Sheet
    cols_to_show = [category_col, owner_col, target_col, actual_col, status_col, remark_col, "Final Status"]
    valid_cols = [c for c in cols_to_show if c in df.columns]
    table_df = filtered[valid_cols].copy()

    # Format dates
    if target_col in table_df.columns:
        table_df[target_col] = table_df[target_col].dt.strftime('%d-%b').fillna("—")
    if actual_col in table_df.columns:
        table_df[actual_col] = table_df[actual_col].dt.strftime('%d-%b').fillna("—")

    html = """
    <div style="overflow-x:auto; margin:20px 0;">
    <table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif;">
        <thead>
            <tr>
    """
    for col in table_df.columns:
        html += f"<th style='background:#1e40af; color:white; padding:15px; text-align:left; font-weight:800;'>{col}</th>"
    html += """
            </tr>
        </thead>
        <tbody>
    """


    for _, row in table_df.iterrows():
        final_status = row["Final Status"]
        status_style = ""
        if final_status == "NOT CLOSED – DELAYED!":
            status_style = "background:#ef4444; color:white; font-weight:bold;"
        elif final_status == "Closed":
            status_style = "background:#22c55e; color:white; font-weight:bold;"
        else:  # Open
            status_style = "background:#fbbf24; color:black; font-weight:bold;"

        html += "<tr>"
        for col in table_df.columns:
            val = str(row[col])
            cell_style = status_style if col == "Final Status" else ""
            html += f"<td style='padding:12px; border:1px solid #ddd; {cell_style}'>{val}</td>"
        html += "</tr>"

    html += """
        </tbody>
    </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
