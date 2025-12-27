import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    # Back button
    if st.button("← Back to Dashboard", key="back_merlin_mom"):
        if 'dashboard' in st.session_state:
            del st.session_state.dashboard
        st.rerun()

    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSWMp9BS_dmgqDQfsvaT525XtS0yZk4OcBm16soaIlZa6qgAmeGS4UncOBB5l_K9pX0czG2IrHsohte/pub?gid=1982980723&single=true&output=csv"

    def load_data():
        df = pd.read_csv(CSV_URL)
        df = df.dropna(how='all').reset_index(drop=True)
        df = df.fillna("—")
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    # Manual refresh
    col1, col2 = st.columns([1, 9])
    with col1:
        if st.button("🔄 Refresh"):
            st.rerun()

    df = load_data()

    # Beautiful Header
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background:linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%); color:white; border-radius:16px; margin-bottom:10px; box-shadow: 0 12px 30px rgba(124,62,237,0.3);">
        <h1 style="margin:0; font-size:2.4rem; font-weight:800;">📝 MERLIN - Minutes of Meeting (MOM)</h1>
        <p style="margin:10px 0 0 0; font-size:1.1rem;">
            Updated: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')} • Auto-refresh every {REFRESH_INTERVAL}s
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Meeting Header
    st.markdown("""
    <div style="background:#f0fdf4; padding:20px; border-radius:16px; margin:15px 0; border-left:6px solid #22c55e; box-shadow:0 4px 20px rgba(0,0,0,0.08);">
        <h2 style="text-align:center; color:#166534; font-size:1.5rem; margin:0 0 10px 0;">Merlin NA Project NPI Meeting</h2>
        <h3 style="text-align:center; color:#0c4a6e; font-size:1.2rem; margin:5px 0;">Schedule Date: 14-Nov-2025</h3>
        <div style="display:flex; justify-content:center; gap:100px; margin-top:10px; flex-wrap:wrap;">
            <div style="text-align:center;">
                <p style="font-weight:bold; color:#1e40af; margin:0;">Dixon</p>
                <p style="margin:3px 0 0 0; color:#64748b;">Subrat, Prabhat</p>
            </div>
            <div style="text-align:center;">
                <p style="font-weight:bold; color:#1e40af; margin:0;">Moto</p>
                <p style="margin:3px 0 0 0; color:#64748b;">Dharmpal, Kawaljeet, Himanshu puri, Hemant, Praveen</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Column detection
    sno_col = next((c for c in df.columns if "s.no" in c.lower() or "sno" in c.lower()), None)
    date_col = next((c for c in df.columns if "date" in c.lower() and "target" not in c.lower()), None)
    open_point_col = next((c for c in df.columns if "open point" in c.lower() or "open" in c.lower()), None)
    resp_col = next((c for c in df.columns if "resp" in c.lower()), None)
    target_date_col = next((c for c in df.columns if "target date" in c.lower() or "target dt" in c.lower()), None)
    status_col = next((c for c in df.columns if "status" in c.lower()), None)
    remarks_col = next((c for c in df.columns if "remark" in c.lower() or "remarks" in c.lower()), None)

    required = [open_point_col, resp_col, status_col]
    if not all(required):
        st.error("Required MOM columns not found in sheet.")
        st.stop()

    # === FILTERS AT TOP CENTER ===
    #st.markdown("<h3 style='text-align:center; color:#7c3aed; margin:50px 0 20px 0;'>🔍 Filters</h3>", unsafe_allow_html=True)

    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1])

    with filter_col1:
        if resp_col:
            resp_options = ["All"] + sorted(df[resp_col].dropna().unique().tolist())
            chosen_resp = st.selectbox("Responsible Person", resp_options, index=0, key="mom_resp_top")

    with filter_col2:
        status_options = ["All", "Closed", "Open"]
        chosen_status = st.selectbox("Status", status_options, index=0, key="mom_status_top")

    with filter_col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear Filters", key="clear_mom_top"):
            st.rerun()

    # Apply filters
    filtered = df.copy()

    if resp_col and chosen_resp != "All":
        filtered = filtered[filtered[resp_col] == chosen_resp]

    if chosen_status != "All":
        filtered = filtered[filtered[status_col].astype(str).str.contains(chosen_status, case=False, na=False)]

    # Table
    cols_to_show = [sno_col, date_col, open_point_col, resp_col, target_date_col, status_col, remarks_col]
    valid_cols = [c for c in cols_to_show if c is not None]
    table_df = filtered[valid_cols].copy()

    # Beautiful Table with Color-Coded Status
    html = """
    <div style="overflow-x:auto; margin:40px 0;">
    <table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif;">
        <thead>
            <tr>
                <th style='background:#22c55e; color:white; padding:15px; text-align:center; font-weight:800;'>S.No</th>
                <th style='background:#22c55e; color:white; padding:15px; text-align:center; font-weight:800;'>Date</th>
                <th style='background:#22c55e; color:white; padding:15px; text-align:left; font-weight:800; width:35%;'>Open Point List</th>
                <th style='background:#22c55e; color:white; padding:15px; text-align:center; font-weight:800;'>Resp.</th>
                <th style='background:#22c55e; color:white; padding:15px; text-align:center; font-weight:800;'>Target Date</th>
                <th style='background:#22c55e; color:white; padding:15px; text-align:center; font-weight:800;'>Status</th>
                <th style='background:#22c55e; color:white; padding:15px; text-align:left; font-weight:800;'>Remarks</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in table_df.iterrows():
        status = str(row.get(status_col, "—")).strip()
        status_lower = status.lower()

        if "closed" in status_lower:
            status_cell = f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center; background:#d1fae5; color:#065f46; font-weight:bold;'>{status}</td>"
        elif "open" in status_lower:
            status_cell = f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center; background:#fee2e2; color:#991b1b; font-weight:bold;'>{status}</td>"
        else:
            status_cell = f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center; background:#fffbeb; color:#92400e; font-weight:bold;'>{status}</td>"

        html += "<tr>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center;'>{row.get(sno_col, '—')}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center;'>{row.get(date_col, '—')}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0;'>{row.get(open_point_col, '—')}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center;'>{row.get(resp_col, '—')}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center;'>{row.get(target_date_col, '—')}</td>"
        html += status_cell
        html += f"<td style='padding:12px; border:1px solid #e2e8f0;'>{row.get(remarks_col, '—')}</td>"
        html += "</tr>"

    html += """
        </tbody>
    </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    # Sidebar - Clean (only success & download)
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