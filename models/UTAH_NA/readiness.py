import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    # Back button to return to model selection (app.py)
    if st.button("← Back to Dashboard", key="back_utah_readiness"):
        if 'dashboard' in st.session_state:
            del st.session_state.dashboard
        st.rerun()

    #st.title("UTAH NA - Process Readiness Tracker")

    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQBqDIx_ZBSYN7RaWxCIjHMZeFBkMhQaKcmc8mvq9KrE-Z1EFeaIsC1B4Fmw_wE_1NbzsConI04b6o0/pub?gid=1841630466&single=true&output=csv"

    @st.cache_data(ttl=REFRESH_INTERVAL)
    def load_data():
        df = pd.read_csv(CSV_URL)
        df = df.dropna(how='all').reset_index(drop=True)
        df = df.fillna("—")
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    df = load_data()

    # Beautiful Header
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background:linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%); color:white; border-radius:16px; margin-bottom:30px; box-shadow: 0 12px 30px rgba(29,78,216,0.3);">
        <h1 style="margin:0; font-size:2.4rem; font-weight:800;">UTAH NA</h1>
        <p style="margin:10px 0 0 0; font-size:1.1rem;">
            Updated: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')} • Auto-refresh every {REFRESH_INTERVAL}s
        </p>
    </div>
    """, unsafe_allow_html=True)


    st.markdown("""
    <div style="background:#f0f9ff; padding:15px; border-radius:20px; margin:40px 0; box-shadow:0 8px 30px rgba(0,0,0,0.1); border:1px solid #bae6fd;">
        <div style="text-align:center;">
            <h3 style="color:#0c4a6e; font-size:1.8rem; margin:0 0 20px 0; font-weight:700;"> Timelines </h3>
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



    # Column detection
    category_col = next((c for c in df.columns if "process category" in c.lower()), df.columns[0])
    sub_col = next((c for c in df.columns if "sub" in c.lower()), None)
    owner_col = next((c for c in df.columns if "owner" in c.lower()), None)
    target_col = next((c for c in df.columns if "target" in c.lower()), None)
    status_col = next((c for c in df.columns if "status" in c.lower()), None)
    remark_col = next((c for c in df.columns if "remark" in c.lower() or "remarks" in c.lower()), None)

    # Status calculation
    if target_col:
        df[target_col] = pd.to_datetime(df[target_col], errors='coerce', dayfirst=True)
    today = pd.Timestamp.today().normalize()

    def get_final_status(row):
        closed = status_col and pd.notna(row.get(status_col)) and str(row[status_col]).strip().lower() in ["closed", "close", "done"]
        overdue = target_col and pd.notna(row.get(target_col)) and row[target_col].normalize() < today
        if closed and not overdue: return "Closed On Time"
        if closed and overdue: return "Closed (Late)"
        if overdue: return "NOT CLOSED – DELAYED!"
        return "Open"

    df["Final Status"] = df.apply(get_final_status, axis=1)

    # Metric Cards
    delayed = len(df[df["Final Status"].str.contains("DELAYED")])
    open_count = len(df[df["Final Status"] == "Open"])
    closed = len(df[~df["Final Status"].str.contains("Open|DELAYED")])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style='background:#ef4444; color:white; padding:15px 20px; border-radius:16px; text-align:center; box-shadow:0 8px 20px rgba(239,68,68,0.3); height:110px; display:flex; flex-direction:column; justify-content:center;'>
            <p style='margin:0; font-size:1.5rem; font-weight:700;'>Delayed</p>
            <h2 style='margin:6px 0 0 0; font-size:1.6rem; font-weight:1000;'>{delayed}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='background:#fbbf24; color:white; padding:15px 20px; border-radius:16px; text-align:center; box-shadow:0 8px 20px rgba(251,191,36,0.3); height:110px; display:flex; flex-direction:column; justify-content:center;'>
            <p style='margin:0; font-size:1.5rem; font-weight:700;'>Open</p>
            <h2 style='margin:6px 0 0 0; font-size:1.6rem; font-weight:1000;'>{open_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style='background:#22c55e; color:white; padding:15px 20px; border-radius:16px; text-align:center; box-shadow:0 8px 20px rgba(34,197,94,0.3); height:110px; display:flex; flex-direction:column; justify-content:center;'>
            <p style='margin:0; font-size:1.5rem; font-weight:700;'>Closed</p>
            <h2 style='margin:6px 0 0 0; font-size:1.6rem; font-weight:1000;'>{closed}</h2>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    # Filters
    col1, col2, col3 = st.columns(3)
    filtered = df.copy()

    with col1:
        if owner_col:
            owners = ["All"] + sorted(filtered[owner_col].dropna().unique().tolist())
            chosen_owner = st.selectbox("👤 Owner", owners, key="owner_ready_utah")
            if chosen_owner != "All":
                filtered = filtered[filtered[owner_col] == chosen_owner]

    with col2:
        categories = ["All"] + sorted(filtered[category_col].dropna().unique().tolist())
        chosen_cat = st.selectbox("📋 Process Category", categories, key="cat_ready_utah")
        if chosen_cat != "All":
            filtered = filtered[filtered[category_col] == chosen_cat]

    with col3:
        view = st.selectbox("🔍 View", ["All Items", "Only Delayed", "Only Open", "Only Closed"], key="view_ready_utah")
        if view == "Only Delayed":
            filtered = filtered[filtered["Final Status"].str.contains("DELAYED")]
        elif view == "Only Open":
            filtered = filtered[filtered["Final Status"] == "Open"]
        elif view == "Only Closed":
            filtered = filtered[~filtered["Final Status"].str.contains("Open|DELAYED")]

    # Alert
    urgent = len(filtered[filtered["Final Status"].str.contains("DELAYED")])
    if urgent:
        st.error(f"🚨 URGENT: {urgent} items DELAYED & NOT CLOSED!")
    else:
        st.success("✅ All items are On Track or Closed")

    # Beautiful HTML Table with grouped categories
    cols_to_show = [category_col, sub_col, owner_col, target_col, status_col, remark_col, "Final Status"]
    valid_cols = [c for c in cols_to_show if c and c in filtered.columns]
    table_df = filtered[valid_cols].reset_index(drop=True)

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

    prev_cat = None
    for _, row in table_df.iterrows():
        status = row["Final Status"]
        status_style = ""
        if "DELAYED" in status:
            status_style = "background:#ef4444; color:white; font-weight:bold;"
        elif "Late" in status:
            status_style = "background:#86efac; color:white; font-weight:bold;"
        elif "On Time" in status:
            status_style = "background:#22c55e; color:white; font-weight:bold;"
        elif status == "Open":
            status_style = "background:#fbbf24; color:white; font-weight:bold;"
        html += "<tr>"
        for col in table_df.columns:
            val = str(row[col])
            if col == category_col:
                cell_content = "" if val == prev_cat else val
                prev_cat = val if cell_content else prev_cat
            else:
                cell_content = val
            cell_style = status_style if col == "Final Status" else ""
            html += f"<td style='padding:12px; border:1px solid #ddd; {cell_style}'>{cell_content}</td>"
        html += "</tr>"

    html += """
        </tbody>
    </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.success("🎯 UTAH NA")
        st.download_button(
            "📥 Download Current View",
            table_df.to_csv(index=False).encode(),
            "utah_na_readiness.csv",
            "text/csv"
        )

if __name__ == "__main__":
    main()