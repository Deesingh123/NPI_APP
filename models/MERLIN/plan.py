import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    # Back button
    #if st.button("← Back to Dashboard", key="back_merlin_plan"):
        #st.rerun()

    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSUKAu7fJg3Oi9Q8_ffen20iCKteQCKLAXCrAVf369XD7zWGF_E3WNko47pUhWLz865B4NHWMFYKEaS/pub?gid=1031879361&single=true&output=csv"

    @st.cache_data(ttl=REFRESH_INTERVAL)
    def load_data():
        df = pd.read_csv(CSV_URL)
        df = df.dropna(how='all').reset_index(drop=True)
        df = df.fillna("—")
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    # Manual refresh button
    #col1, col2 = st.columns([1, 9])
    #with col1:
        #if st.button("🔄 Refresh"):
            #st.rerun()

    df = load_data()

    # Beautiful Header
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background:linear-gradient(135deg, #c2410c 0%, #ea580c 100%); color:white; border-radius:16px; margin-bottom:20px; box-shadow: 0 12px 30px rgba(194,65,12,0.3);">
        <h1 style="margin:0; font-size:2.4rem; color:white; font-weight:800;"> MERLIN Plan</h1>
        <p style="margin:10px 0 0 0; font-size:1.1rem;">
            Updated: {datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")} • Auto-refresh every {REFRESH_INTERVAL}s
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Robust column detection
    def find_column(columns, keywords):
        for col in columns:
            col_lower = col.lower().strip()
            if any(k.lower() in col_lower for k in keywords):
                return col
        return None

    wbs_col = find_column(df.columns, ["wbs"])
    milestone_col = find_column(df.columns, ["milestone"])
    plan_col = find_column(df.columns, ["plan date", "plan"])
    actual_col = find_column(df.columns, ["actual date", "actual"])
    remarks_col = find_column(df.columns, ["remarks", "remark"])

    # Safety check
    if not all([wbs_col, milestone_col, plan_col]):
        st.error("Required columns (WBS, Milestone, Plan Date) not found in sheet.")
        st.stop()

    # Format dates - Explicit '%d-%b' for "1-Nov", "13-Dec", etc.
    df_display = df.copy()
    if plan_col in df_display.columns:
        df_display[plan_col] = df_display[plan_col].replace("—", pd.NA)
        df_display[plan_col] = pd.to_datetime(df_display[plan_col], format='%d-%b', errors='coerce')
        df_display[plan_col] = df_display[plan_col].dt.strftime('%d-%b').fillna("—")
    if actual_col in df_display.columns:
        df_display[actual_col] = df_display[actual_col].replace("—", pd.NA)
        df_display[actual_col] = pd.to_datetime(df_display[actual_col], format='%d-%b', errors='coerce')
        df_display[actual_col] = df_display[actual_col].dt.strftime('%d-%b').fillna("—")

    # Beautiful HTML Table with WBS grouping (blank on repeat)
    cols_to_show = [wbs_col, milestone_col, plan_col, actual_col, remarks_col]
    valid_cols = [c for c in cols_to_show if c in df_display.columns]
    table_df = df_display[valid_cols]



    html = """
    <div style="overflow-x:auto; margin:20px 0;">
    <table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif;">
        <thead>
            <tr>
                <th style='background:#7c3aed; color:white; padding:15px; text-align:left; font-weight:700; font-size:1.05rem;'>WBS</th>
                <th style='background:#7c3aed; color:white; padding:15px; text-align:left; font-weight:700; font-size:1.05rem;'>Milestone</th>
                <th style='background:#7c3aed; color:white; padding:15px; text-align:center; font-weight:700; font-size:1.05rem;'>Plan Date</th>
                <th style='background:#7c3aed; color:white; padding:15px; text-align:center; font-weight:700; font-size:1.05rem;'>Actual Date</th>
                <th style='background:#7c3aed; color:white; padding:15px; text-align:left; font-weight:700; font-size:1.05rem;'>Remarks</th>
            </tr>
        </thead>
        <tbody>
    """

    prev_wbs = None
    for _, row in table_df.iterrows():  # row is now the Series
        wbs_val = row[wbs_col]
        display_wbs = "" if wbs_val == prev_wbs else wbs_val
        prev_wbs = wbs_val

        html += "<tr style='background:#ffffff;'>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0;'>{display_wbs}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0;'>{row[milestone_col]}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center;'>{row.get(plan_col, '—')}</td>"
        html += f"<td style='padding:12px; border:1px solid #e2e8f0; text-align:center;'>{row.get(actual_col, '—')}</td>"
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
        st.success("🚀 MERLIN Project Plan")
        st.download_button(
            "📥 Download Data",
            df.to_csv(index=False).encode(),
            "merlin_project_plan.csv",
            "text/csv"
        )

if __name__ == "__main__":
    main()


