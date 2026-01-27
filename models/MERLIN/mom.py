import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSWMp9BS_dmgqDQfsvaT525XtS0yZk4OcBm16soaIlZa6qgAmeGS4UncOBB5l_K9pX0czG2IrHsohte/pub?gid=1982980723&single=true&output=csv"

    @st.cache_data(ttl=REFRESH_INTERVAL)
    def load_data():
        df = pd.read_csv(CSV_URL)
        df = df.dropna(how='all').reset_index(drop=True)
        df = df.fillna("—")
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    df = load_data()

    # Header (unchanged)
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background:linear-gradient(135deg,#4338ca 0%, #a78bfa 100%); color:white; border-radius:16px; margin-bottom:15px; box-shadow: 0 12px 30px rgba(124,62,237,0.3);">
        <h1 style="margin:0; font-size:2.4rem; color:white; font-weight:1000;"> MERLIN Minutes of Meeting(MOM)</h1>
        <p style="margin:10px 0 0 0; font-size:1.1rem;">
            Updated: {datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")} • Auto-refresh every {REFRESH_INTERVAL}s
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Meeting Info (unchanged)
    st.markdown("""
    <div style="background:#f0fdf4; padding:15px; border-radius:16px; margin:10px 0; border-left:6px #22c55e; box-shadow:0 4px 20px rgba(0,0,0,0.08);">
        <h3 style="text-align:center; color:#0c4a6e; font-size:1.2rem; margin:5px 0;">Meeting Schedule Date: 12-Jan-2026</h3>
        <div style="display:flex; justify-content:center; gap:100px; margin-top:10px; flex-wrap:wrap;">
            <div style="text-align:center;">
                <p style="font-weight:bold; color:#1e40af; margin:0;">Dixon</p>
                <p style="margin:3px 0 0 0; color:#64748b;">Subrat, Risabh</p>
            </div>
            <div style="text-align:center;">
                <p style="font-weight:bold; color:#1e40af; margin:0;">Moto</p>
                <p style="margin:3px 0 0 0; color:#64748b;">Kawaljeet, Sachin,Janki,Saubhagya, Saurov,Yang yang24 ,Zheng Zheng3,Zhongyu</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Column detection (unchanged)
    date_col = next((c for c in df.columns if "date" in c.lower() and "target" not in c.lower()), None)
    open_point_col = next((c for c in df.columns if "open point" in c.lower() or "open" in c.lower()), None)
    resp_col = next((c for c in df.columns if "resp" in c.lower()), None)
    target_date_col = next((c for c in df.columns if "target date" in c.lower() or "target dt" in c.lower()), None)
    status_col = next((c for c in df.columns if "status" in c.lower()), None)
    remarks_col = next((c for c in df.columns if "remark" in c.lower() or "remarks" in c.lower()), None)

    if not all([open_point_col, resp_col, status_col]):
        st.error("Required MOM columns not found in sheet.")
        st.stop()

    # Count Cards (unchanged)
    total_count = len(df)
    open_count = len(df[df[status_col].astype(str).str.contains("open", case=False, na=False)])
    closed_count = len(df[df[status_col].astype(str).str.contains("closed", case=False, na=False)])
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style='background:#7c3aed; padding:30px 20px; border-radius:20px; text-align:center; height:140px;
                    box-shadow:0 8px 25px rgba(0,0,0,0.08); display:flex; flex-direction:column; justify-content:center; align-items:center;'>
            <p style='margin:0; font-size:1.6rem; font-weight:700; color:white;'>Total Actions</p>
            <h2 style='margin:8px 0 0 0; font-size:3.0rem; font-weight:900; color:white;'>{total_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='background:#ec4899; padding:30px 20px; border-radius:20px; text-align:center; height:140px;
                    box-shadow:0 8px 25px rgba(0,0,0,0.08); display:flex; flex-direction:column; justify-content:center; align-items:center;'>
            <p style='margin:0; font-size:1.6rem; font-weight:700; color:white;'>Open</p>
            <h2 style='margin:8px 0 0 0; font-size:3.0rem; font-weight:900; color:white;'>{open_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div style='background:#10b981; padding:30px 20px; border-radius:20px; text-align:center; height:140px;
                    box-shadow:0 8px 25px rgba(0,0,0,0.08); display:flex; flex-direction:column; justify-content:center; align-items:center;'>
            <p style='margin:0; font-size:1.6rem; font-weight:700; color:white;'>Closed</p>
            <h2 style='margin:8px 0 0 0; font-size:3.0rem; font-weight:900; color:white;'>{closed_count}</h2>
        </div>
        """, unsafe_allow_html=True)

    # Filters (unchanged)
    fcol1, fcol2 = st.columns([2, 2])
    with fcol1:
        if resp_col:
            resp_options = ["All"] + sorted(df[resp_col].dropna().unique().tolist())
            chosen_resp = st.selectbox("Responsible Person", resp_options, index=0, key="mom_resp_filter_final")
    with fcol2:
        chosen_status = st.selectbox("Status", ["All", "Closed", "Open"], index=0, key="mom_status_filter_final")

    # Apply filters
    filtered = df.copy()
    if resp_col and chosen_resp != "All":
        filtered = filtered[filtered[resp_col] == chosen_resp]
    if chosen_status != "All":
        filtered = filtered[filtered[status_col].astype(str).str.contains(chosen_status, case=False, na=False)]

    # Table columns
    cols_to_show = [date_col, open_point_col, resp_col, target_date_col, status_col, remarks_col]
    valid_cols = [c for c in cols_to_show if c is not None]
    table_df = filtered[valid_cols].copy()

    # ── MORE COMPACT TABLE ──────────────────────────────────────────────────
    html = """
    <div style="overflow-x:auto; margin:25px 0;">
    <table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif; font-size:0.92rem;">
        <thead>
            <tr>
                <th style='background:#22c55e; color:white; padding:8px 6px; text-align:center; font-weight:800;'>Date</th>
                <th style='background:#22c55e; color:white; padding:8px 10px; text-align:left; font-weight:800; width:38%;'>Open Point List</th>
                <th style='background:#22c55e; color:white; padding:8px 6px; text-align:center; font-weight:800;'>Resp.</th>
                <th style='background:#22c55e; color:white; padding:8px 6px; text-align:center; font-weight:800;'>Target Date</th>
                <th style='background:#22c55e; color:white; padding:8px 6px; text-align:center; font-weight:800;'>Status</th>
                <th style='background:#22c55e; color:white; padding:8px 10px; text-align:left; font-weight:800;'>Remarks</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in table_df.iterrows():
        status = str(row.get(status_col, "—")).strip()
        status_lower = status.lower()
        if "closed" in status_lower:
            status_cell = f"<td style='padding:7px 6px; border:1px solid #e2e8f0; text-align:center; background:#d1fae5; color:#065f46; font-weight:bold;'>{status}</td>"
        elif "open" in status_lower:
            status_cell = f"<td style='padding:7px 6px; border:1px solid #e2e8f0; text-align:center; background:#fee2e2; color:#991b1b; font-weight:bold;'>{status}</td>"
        else:
            status_cell = f"<td style='padding:7px 6px; border:1px solid #e2e8f0; text-align:center; background:#fffbeb; color:#92400e; font-weight:bold;'>{status}</td>"

        html += "<tr>"
        html += f"<td style='padding:7px 6px; border:1px solid #e2e8f0; text-align:center;'>{row.get(date_col, '—')}</td>"
        html += f"<td style='padding:7px 10px; border:1px solid #e2e8f0;'>{row.get(open_point_col, '—')}</td>"
        html += f"<td style='padding:7px 6px; border:1px solid #e2e8f0; text-align:center;'>{row.get(resp_col, '—')}</td>"
        html += f"<td style='padding:7px 6px; border:1px solid #e2e8f0; text-align:center;'>{row.get(target_date_col, '—')}</td>"
        html += status_cell
        html += f"<td style='padding:7px 10px; border:1px solid #e2e8f0;'>{row.get(remarks_col, '—')}</td>"
        html += "</tr>"

    html += """
        </tbody>
    </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    # Sidebar (unchanged)
    with st.sidebar:
        st.success("📝 MERLIN MOM")
        st.download_button(
            "📥 Download MOM Data",
            df.to_csv(index=False).encode(),
            "merlin_mom_data.csv",
            "text/csv"
        )

if __name__ == "__main__":
    main()
