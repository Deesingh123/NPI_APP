import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    # Back button
    if st.button("← Back to Dashboard", key="back_merlin_kpi"):
        if 'dashboard' in st.session_state:
            del st.session_state.dashboard
        st.rerun()

    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTsS6PyxZ7Q07fxpaCmc-0mMowukVYiFA5EyDUP6BmFhXniA53bM30drIZnhEjLSPVHzuaqS4jjlLwb/pub?gid=1065751321&single=true&output=csv"

    def load_data():
        df = pd.read_csv(CSV_URL)
        df = df.dropna(how='all').reset_index(drop=True)
        df = df.fillna("—")
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    # Manual refresh
    #col1, col2 = st.columns([1, 9])
    #with col1:
        #if st.button("🔄 Refresh"):
            #st.rerun()

    df = load_data()

    # Beautiful Header - MERLIN Purple Theme
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background:linear-gradient(135deg, #d97706 0%, #f59e0b 100%); color:white; border-radius:16px; margin-bottom:20px; box-shadow: 0 12px 30px rgba(124,62,237,0.3);">
        <h1 style="margin:0; font-size:2.4rem; color:white; font-weight:1000;"> MERLIN KPI</h1>
        <p style="margin:10px 0 0 0; font-size:1.1rem;">
            Updated: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')} • Auto-refresh every {REFRESH_INTERVAL}s
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Flexible column detection (handles apostrophe, spaces, case)
    def find_col(cols, keywords):
        for c in cols:
            if any(k.lower() in c.lower() for k in keywords):
                return c
        return None

    kpi_col = find_col(df.columns, ["KPI", "KPI's", "KPIs"])
    target_col = find_col(df.columns, ["Target"])
    actual_col = find_col(df.columns, ["Actual"])
    action_col = find_col(df.columns, ["Action plan", "Action"])
    target_dt_col = find_col(df.columns, ["Target Dt", "Target Date"])
    resp_col = find_col(df.columns, ["Resp.", "Resp", "Responsible"])
    remarks_col = find_col(df.columns, ["Remarks", "Remark"])

    # Safety check
    required = [kpi_col, target_col, actual_col]
    if not all(required):
        st.error(f"Required columns not found. Found: {df.columns.tolist()}")
        st.stop()

    # Select columns
    cols_to_show = [kpi_col, target_col, actual_col, action_col, target_dt_col, resp_col, remarks_col]
    valid_cols = [c for c in cols_to_show if c is not None]
    table_df = df[valid_cols].copy()

    # Beautiful KPI Table - Yellow Target/Actual Header
    html = """
    <div style="overflow-x:auto; margin:20px 0;">
    <table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif;">
        <thead>
            <tr>
                <th style='background:#7c3aed; color:white; padding:15px; text-align:left; font-weight:800; width:28%;'>KPI's</th>
                <th style='background:#fbbf24; color:black; padding:15px; text-align:center; font-weight:800;'>Target</th>
                <th style='background:#fbbf24; color:black; padding:15px; text-align:center; font-weight:800;'>Actual</th>
                <th style='background:#e0e7ff; color:#1e40af; padding:15px; text-align:left; font-weight:800;'>Action plan</th>
                <th style='background:#e0e7ff; color:#1e40af; padding:15px; text-align:center; font-weight:800;'>Target Dt</th>
                <th style='background:#e0e7ff; color:#1e40af; padding:15px; text-align:center; font-weight:800;'>Resp.</th>
                <th style='background:#e0e7ff; color:#1e40af; padding:15px; text-align:left; font-weight:800;'>Remarks</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in table_df.iterrows():
        kpi_name = row[kpi_col]
        target = row.get(target_col, "—")
        actual = row.get(actual_col, "—")

        # Light red background if Actual is worse than Target (for % values)
        row_style = ""
        try:
            if "%" in str(target) and "%" in str(actual) and actual != "—":
                t_val = float(str(target).replace("%", "").strip())
                a_val = float(str(actual).replace("%", "").strip())
                if a_val < t_val:
                    row_style = "background:#fee2e2;"
        except:
            pass

        html += f"<tr style='{row_style}'>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0; font-weight:bold;'>{kpi_name}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center; font-weight:bold; color:#166534;'>{target}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center; font-weight:bold; color:#dc2626;'>{actual}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0;'>{row.get(action_col, '—')}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center;'>{row.get(target_dt_col, '—')}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center;'>{row.get(resp_col, '—')}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0;'>{row.get(remarks_col, '—')}</td>"
        html += "</tr>"

    html += """
        </tbody>
    </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.success("📊 MERLIN KPIs")
        st.download_button(
            "📥 Download KPI Data",
            df.to_csv(index=False).encode(),
            "merlin_kpi_data.csv",
            "text/csv"
        )

if __name__ == "__main__":
    main()

