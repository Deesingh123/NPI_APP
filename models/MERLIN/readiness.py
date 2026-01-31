import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQBqDIx_ZBSYN7RaWxCIjHMZeFBkMhQaKcmc8mvq9KrE-Z1EFeaIsC1B4Fmw_wE_1NbzsConI04b6o0/pub?gid=398221268&single=true&output=csv"

    @st.cache_data(ttl=REFRESH_INTERVAL)
    def load_data():
        df = pd.read_csv(CSV_URL)
        df = df.dropna(how='all').reset_index(drop=True)
        df = df.fillna("—")
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    df = load_data()

    # Fill down Process Category (unchanged)
    category_col = next((col for col in df.columns if "process category" in col.lower() or "category" in col.lower()), None)
    if category_col:
        df[category_col] = df[category_col].replace("—", pd.NA)
        df[category_col] = df[category_col].ffill()
        df[category_col] = df[category_col].fillna("No Category")

    # Header (unchanged)
    st.markdown(f"""
    <div style="text-align:center; padding:16px; background:linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%); color:white; border-radius:12px; margin-bottom:12px;">
        <h1 style="margin:0; font-size:2.4rem; color:white; font-weight:800;">Merlin Readiness</h1>
        <p style="margin:8px 0 0 0; font-size:1rem;">
            Updated: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')} • refresh every {REFRESH_INTERVAL}s
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Timeline (unchanged)
    st.markdown("""
    <div style="background:#f0f9ff; padding:15px; border-radius:20px; margin:15px 0; box-shadow:0 8px 30px rgba(0,0,0,0.1); border:1px solid #bae6fd;">
        <div style="text-align:center;">
            <h3 style="color:#0c4a6e; font-size:1.8rem; margin:0 0 15px 0; font-weight:700;"> Timelines </h3>
            <div style="display:flex; justify-content:space-around; flex-wrap:wrap; gap:20px;">
                <div style="text-align:center;">
                    <p style="font-size:1.4rem; font-weight:bold; color:#166534; margin:0;">PVT</p>
                    <p style="font-size:1.2rem; color:#0c4a6e; margin:5px 0 0 0;">16 JAN</p>
                </div>
                <div style="text-align:center;">
                    <p style="font-size:1.4rem; font-weight:bold; color:#0c4a6e; margin:0;">OK2P</p>
                    <p style="font-size:1.2rem; color:#0c4a6e; margin:5px 0 0 0;">23 FEB</p>
                </div>
                <div style="text-align:center;">
                    <p style="font-size:1.4rem; font-weight:bold; color:#0c4a6e; margin:0;">OK2R</p>
                    <p style="font-size:1.2rem; color:#0c4a6e; margin:5px 0 0 0;">16 MAR</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Column detection (unchanged)
    def find_column(columns, keywords):
        for col in columns:
            col_lower = col.lower().strip()
            if any(k.lower() in col_lower for k in keywords):
                return col
        return None

    sub_col      = find_column(df.columns, ["sub activity", "sub"])
    owner_col    = find_column(df.columns, ["owner"])
    target_col   = find_column(df.columns, ["target date", "target"])
    actual_col   = find_column(df.columns, ["actual date", "actual"])
    status_col   = find_column(df.columns, ["status"])
    remark_col   = find_column(df.columns, ["remarks", "remark"])

    essential = [category_col, sub_col, owner_col, target_col, status_col]
    if not all(essential):
        st.error("Essential columns not found in sheet.")
        st.stop()

    # ────────────────────────────────────────────────────────────────
    # IMPORTANT CHANGE: Do NOT convert Target / Actual Date to datetime
    # Keep them as original string → shows exactly as in Google Sheet
    # (no .dt.strftime(), no parsing)
    # ────────────────────────────────────────────────────────────────

    today = pd.Timestamp.today().normalize()

    def get_final_status(row):
        status_val = str(row.get(status_col, '')).strip().lower()
        closed = status_val in ["closed", "close", "done"]
        open_or_ongoing = status_val in ["open", "ongoing", "on going"]

        # For overdue check: only try to compare if it looks like a date we can parse
        try:
            target_str = str(row.get(target_col, '—')).strip()
            if target_str != '—' and '/' in target_str:
                target_date = pd.to_datetime(target_str, format='%m/%d/%Y', errors='coerce')
                overdue = pd.notna(target_date) and target_date < today
            else:
                overdue = False
        except:
            overdue = False

        if closed:
            return "Closed"
        elif open_or_ongoing:
            return "Opened"
        elif overdue:
            return "Delayed"
        else:
            return "Opened"

    df["Final Status"] = df.apply(get_final_status, axis=1)

    # Metrics (unchanged)
    delayed = len(df[df["Final Status"] == "Delayed"])
    opened  = len(df[df["Final Status"] == "Opened"])
    closed  = len(df[df["Final Status"] == "Closed"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style='background:#ef4444;color:white;padding:12px;border-radius:10px;text-align:center;'>
            <p style='margin:0;font-weight:800;font-size:1.3rem;'>Delayed</p>
            <h2 style='margin:4px 0 0 0;color:white;font-size:1.8rem;'>{delayed}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='background:#fbbf24;color:white;padding:12px;border-radius:10px;text-align:center;'>
            <p style='margin:0;font-weight:800;font-size:1.3rem;'>Opened</p>
            <h2 style='margin:4px 0 0 0;color:white;font-size:1.8rem;'>{opened}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style='background:#22c55e;color:white;padding:12px;border-radius:10px;text-align:center;'>
            <p style='margin:0;font-weight:800;font-size:1.3rem;'>Closed</p>
            <h2 style='margin:4px 0 0 0;color:white;font-size:1.8rem;'>{closed}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Filters (unchanged)
    filtered = df.copy()
    col1, col2, col3 = st.columns(3)
    with col1:
        owners = ["All"] + sorted(filtered[owner_col].dropna().unique().tolist())
        chosen_owner = st.selectbox("Owner", owners, key="owner_av")
        if chosen_owner != "All":
            filtered = filtered[filtered[owner_col] == chosen_owner]

    with col2:
        categories = ["All"] + sorted(filtered[category_col].dropna().unique().tolist())
        chosen_cat = st.selectbox("Process Category", categories, key="cat_av")
        if chosen_cat != "All":
            filtered = filtered[filtered[category_col] == chosen_cat]

    with col3:
        view = st.selectbox("View",
                            ["All Items", "Only Delayed", "Only Opened", "Only Closed"],
                            key="view_av")
        if view == "Only Delayed":
            filtered = filtered[filtered["Final Status"] == "Delayed"]
        elif view == "Only Opened":
            filtered = filtered[filtered["Final Status"] == "Opened"]
        elif view == "Only Closed":
            filtered = filtered[filtered["Final Status"] == "Closed"]

    urgent = len(filtered[filtered["Final Status"] == "Delayed"])
    if urgent:
        st.error(f"🚨 {urgent} items DELAYED")
    else:
        st.success("✅ All items are Opened or Closed")

    # Prepare table → dates are kept as original strings
    table_df = filtered.copy()
    # No .dt.strftime() anymore — dates remain exactly as in sheet

    possible_cols = [category_col, sub_col, owner_col, target_col, actual_col, status_col, remark_col, "Final Status"]
    cols_to_show = [c for c in possible_cols if c is not None and c in table_df.columns]
    table_df = table_df[cols_to_show]

    # Compact HTML Table (unchanged styling)
    html = """
    <div style="overflow-x:auto; margin:12px 0;">
    <table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif; font-size:0.88rem; line-height:1.25;">
        <thead>
            <tr style="background:#1e40af; color:white;">
    """

    column_widths = {
        category_col: "10%",
        sub_col: "25%",
        owner_col: "13%",
        target_col: "7%",      # slightly wider for longer date format
        actual_col: "7%",
        status_col: "5%",
        remark_col: "30%",
        "Final Status": "13%"
    }

    for col in table_df.columns:
        width = column_widths.get(col, "12%")
        html += f"<th style='padding:6px 6px; text-align:left; font-weight:700; width:{width}; font-size:0.9rem;'>{col}</th>"

    html += """
            </tr>
        </thead>
        <tbody>
    """

    for _, row in table_df.iterrows():
        final = row["Final Status"]
        row_bg = ""
        text_color = ""

        if final == "Delayed":
            row_bg = "#fef2f2"
            text_color = "#991b1b"
        elif final == "Opened":
            row_bg = "#fffbeb"
            text_color = "#92400e"
        elif final == "Closed":
            row_bg = "#f0fdf4"
            text_color = "#166534"

        html += f"<tr style='background:{row_bg}; color:{text_color};'>"
        for col in table_df.columns:
            val = str(row[col]).replace("\n", "<br>")
            cell_style = ""
            if col == "Final Status":
                if final == "Delayed":
                    cell_style = "background:#ef4444; color:white; font-weight:bold;"
                elif final == "Opened":
                    cell_style = "background:#fbbf24; color:white; font-weight:bold;"
                elif final == "Closed":
                    cell_style = "background:#22c55e; color:white; font-weight:bold;"
            html += f"<td style='padding:6px 6px; border:1px solid #e5e7eb; vertical-align:top; {cell_style}'>{val}</td>"
        html += "</tr>"

    html += """
        </tbody>
    </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    with st.sidebar:
        st.success("🎯 MERLIN")
        st.download_button(
            "📥 Download Current View",
            table_df.to_csv(index=False).encode(),
            "merlin_readiness.csv",
            "text/csv"
        )

if __name__ == "__main__":
    main()
