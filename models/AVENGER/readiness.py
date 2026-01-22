import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    # Back button
    if st.button("← Back to Dashboard", key="back_avenger_readiness"):
        st.rerun()

    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSz6_P0LpHQadhO2FtHbHcAz5t3wl-prjVx_4erMZkwYYlVHwW0sB6uDT_NkmGSxAJgkoglXebCzD1f/pub?gid=1477446268&single=true&output=csv"

    @st.cache_data(ttl=REFRESH_INTERVAL)
    def load_data():
        df = pd.read_csv(CSV_URL)
        df = df.dropna(how='all').reset_index(drop=True)
        df = df.fillna("—")
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    df = load_data()

    # Header
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background:linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%); color:white; border-radius:16px; margin-bottom:15px;">
        <h1 style="margin:0; font-size:2.4rem; color: white; font-weight:800;">AVENGER Readiness</h1>
        <p style="margin:10px 0 0 0; font-size:1.1rem;">
            Updated: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')} • Auto-refresh every {REFRESH_INTERVAL}s
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Timeline (you can update dates if needed)
    st.markdown("""
    <div style="background:#f0f9ff; padding:15px; border-radius:20px; margin:15px 0; box-shadow:0 8px 30px rgba(0,0,0,0.1); border:1px solid #bae6fd;">
        <div style="text-align:center;">
            <h3 style="color:#0c4a6e; font-size:1.8rem; margin:0 0 15px 0; font-weight:700;"> Timelines </h3>
            <div style="display:flex; justify-content:center; gap:80px; flex-wrap:wrap;">
                <div style="text-align:center;">
                    <p style="font-size:1.5rem; font-weight:bold; color:#166534; margin:0;">PVT</p>
                    <p style="font-size:1.3rem; color:#0c4a6e; margin:8px 0 0 0;">23 DEC</p>
                </div>
                <div style="text-align:center;">
                    <p style="font-size:1.5rem; font-weight:bold; color:#0c4a6e; margin:0;">OK2P</p>
                    <p style="font-size:1.3rem; color:#0c4a6e; margin:8px 0 0 0;">15 JAN</p>
                </div>
                <div style="text-align:center;">
                    <p style="font-size:1.5rem; font-weight:bold; color:#0c4a6e; margin:0;">OK2R</p>
                    <p style="font-size:1.3rem; color:#0c4a6e; margin:8px 0 0 0;">27 JAN</p>
                </div>
                <div style="text-align:center;">
                    <p style="font-size:1.5rem; font-weight:bold; color:#0c4a6e; margin:0;">OK2S</p>
                    <p style="font-size:1.3rem; color:#0c4a6e; margin:8px 0 0 0;">05 FEB</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Robust column detection
    def find_column(columns, keywords):
        for col in columns:
            col_lower = col.lower().strip()
            if any(k.lower() in col_lower for k in keywords):
                return col
        return None

    category_col = find_column(df.columns, ["Process Category", "category"])
    sub_col = find_column(df.columns, ["Sub Activity", "sub"])
    owner_col = find_column(df.columns, ["Owner"])
    target_col = find_column(df.columns, ["Target Date", "target"])
    actual_col = find_column(df.columns, ["Actual Date", "actual"])
    status_col = find_column(df.columns, ["Status"])
    remark_col = find_column(df.columns, ["Remarks", "remark"])

    essential = [category_col, sub_col, owner_col, target_col, status_col]
    if not all(essential):
        st.error("Essential columns not found in sheet.")
        st.stop()

    # Date parsing - Handle "15-Oct", "18-Nov", "3-Dec", "NaT", "—"
    if target_col:
        df[target_col] = df[target_col].replace(["—", "NaT", "", "NA"], pd.NA)
        df[target_col] = pd.to_datetime(df[target_col], format='%d-%b', errors='coerce')
    if actual_col:
        df[actual_col] = df[actual_col].replace(["—", "NaT", "", "NA"], pd.NA)
        df[actual_col] = pd.to_datetime(df[actual_col], format='%d-%b', errors='coerce')

    today = pd.Timestamp.today().normalize()



# Final Status Logic - "Ongoing" treated as "Open"
    def get_final_status(row):
        status_val = str(row[status_col]).strip().lower()
        closed = status_val in ["closed", "close", "done"]
        # Treat "ongoing" same as "open"
        open_or_ongoing = status_val in ["open", "ongoing", "on going"]
        overdue = pd.notna(row[target_col]) and row[target_col].normalize() < today

        if closed:
            return "Closed On Time"
        elif open_or_ongoing:
            return "Open"  # Ongoing → Open
        elif overdue:
            return "NOT CLOSED – DELAYED"
        else:
            return "Open"

    df["Final Status"] = df.apply(get_final_status, axis=1)

    # Metric Cards - Ongoing counted in Open
    delayed = len(df[df["Final Status"].str.contains("DELAYED")])
    open_count = len(df[df["Final Status"] == "Open"])  # Includes Ongoing
    closed = len(df[df["Final Status"] == "Closed On Time"])


    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style='background:#ef4444; color:white; padding:15px 20px; border-radius:16px; text-align:center; box-shadow:0 8px 20px rgba(239,68,68,0.3); height:110px; display:flex; flex-direction:column; justify-content:center; align-items:center;'>
            <p style='margin:0; font-size:1.5rem; font-weight:700; line-height:1.2;'>Delayed</p>
            <h2 style='margin:6px 0 0 0; font-size:1.9rem; color:white; text-align:center; font-weight:1000; line-height:1;'>{delayed}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='background:#fbbf24; color:white; padding:20px; border-radius:16px; text-align:center; box-shadow:0 8px 20px rgba(251,191,36,0.3); height:110px; display:flex; flex-direction:column; justify-content:center; align-items:center;'>
            <p style='margin:0; font-size:1.5rem; font-weight:700; line-height:1.2;'>Opened</p>
            <h2 style='margin:6px 0 0 0;text-align: center; color:white; font-size:1.9rem; font-weight:1000; line-height:1;'>{open_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style='background:#22c55e; color:white; padding:15px 20px; border-radius:16px; text-align:center; box-shadow:0 8px 20px rgba(34,197,94,0.3); height:110px; display:flex; flex-direction:column; justify-content:center; align-items:center;'>
            <p style='margin:0; font-size:1.5rem; font-weight:700; line-height:1.2;'>Closed</p>
            <h2 style='margin:6px 0 0 0;color:white; font-size:1.9rem; font-weight:1000; line-height:1;'>{closed}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Filters
    filtered = df.copy()
    col1, col2, col3 = st.columns(3)

    with col1:
        if owner_col:
            owners = ["All"] + sorted(filtered[owner_col].dropna().unique().tolist())
            chosen_owner = st.selectbox("👤 Owner", owners, key="owner_avenger")
            if chosen_owner != "All":
                filtered = filtered[filtered[owner_col] == chosen_owner]

    with col2:
        categories = ["All"] + sorted(filtered[category_col].dropna().unique().tolist())
        chosen_cat = st.selectbox("📋 Process Category", categories, key="cat_avenger")
        if chosen_cat != "All":
            filtered = filtered[filtered[category_col] == chosen_cat]

    with col3:
        view = st.selectbox("🔍 View", ["All Items", "Only Delayed", "Only Open", "Only Closed"], key="view_avenger")
        if view == "Only Delayed":
            filtered = filtered[filtered["Final Status"].str.contains("DELAYED")]
        elif view == "Only Open":
            filtered = filtered[filtered["Final Status"] == "Open"]
        elif view == "Only Closed":
            filtered = filtered[filtered["Final Status"] == "Closed On Time"]

    # Alert
    urgent = len(filtered[filtered["Final Status"].str.contains("DELAYED")])
    if urgent:
        st.error(f"🚨 URGENT: {urgent} items DELAYED & NOT CLOSED")
    else:
        st.success("✅ All items are On Track or Closed")

    # Format dates for display
    table_df = filtered.copy()
    if target_col in table_df.columns:
        table_df[target_col] = table_df[target_col].dt.strftime('%d-%b').fillna("—")
    if actual_col in table_df.columns:
        table_df[actual_col] = table_df[actual_col].dt.strftime('%d-%b').fillna("—")

    # Columns order
    cols_to_show = [category_col, sub_col, owner_col, target_col, actual_col, status_col, remark_col, "Final Status"]
    valid_cols = [c for c in cols_to_show if c in table_df.columns]
    table_df = table_df[valid_cols]

    # HTML Table - Show category on every row
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

# In HTML table - "Open" (including Ongoing) gets yellow
    for _, row in table_df.iterrows():
        final_status = row["Final Status"]
        status_style = ""
        if "DELAYED" in final_status:
            status_style = "background:#ef4444; color:white; font-weight:bold;"
        elif final_status == "Open":  # Covers both Open and Ongoing
            status_style = "background:#fbbf24; color:white; font-weight:bold;"
        elif final_status == "Closed On Time":
            status_style = "background:#22c55e; color:white; font-weight:bold;"

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

    # Sidebar
    with st.sidebar:
        st.success("🎯 AVENGER")
        st.download_button(
            "📥 Download Current View",
            table_df.to_csv(index=False).encode(),
            "avenger_readiness.csv",
            "text/csv"
        )

if __name__ == "__main__":
    main()
