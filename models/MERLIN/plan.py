import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSUKAu7fJg3Oi9Q8_ffen20iCKteQCKLAXCrAVf369XD7zWGF_E3WNko47pUhWLz865B4NHWMFYKEaS/pub?gid=1031879361&single=true&output=csv"

    @st.cache_data(ttl=REFRESH_INTERVAL)
    def load_data():
        df = pd.read_csv(CSV_URL)
        df = df.dropna(how='all').reset_index(drop=True)
        df = df.fillna("—")
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    df = load_data()

    # Beautiful Header (unchanged)
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background:linear-gradient(135deg, #c2410c 0%, #ea580c 100%); color:white; border-radius:16px; margin-bottom:20px; box-shadow: 0 12px 30px rgba(194,65,12,0.3);">
        <h1 style="margin:0; font-size:2.4rem; color:white; font-weight:800;"> MERLIN Plan</h1>
        <p style="margin:10px 0 0 0; font-size:1.1rem;">
            Updated: {datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")} • Auto-refresh every {REFRESH_INTERVAL}s
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Robust column detection (unchanged)
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

    if not all([wbs_col, milestone_col, plan_col]):
        st.error("Required columns (WBS, Milestone, Plan Date) not found in sheet.")
        st.stop()

    # Format dates
    df_display = df.copy()
    if plan_col in df_display.columns:
        df_display[plan_col] = df_display[plan_col].replace("—", pd.NA)
        df_display[plan_col] = pd.to_datetime(df_display[plan_col], format='%d-%b', errors='coerce')
        df_display[plan_col] = df_display[plan_col].dt.strftime('%d-%b').fillna("—")
    if actual_col in df_display.columns:
        df_display[actual_col] = df_display[actual_col].replace("—", pd.NA)
        df_display[actual_col] = pd.to_datetime(df_display[actual_col], format='%d-%b', errors='coerce')
        df_display[actual_col] = df_display[actual_col].dt.strftime('%d-%b').fillna("—")

    # ── COMPACT TABLE with adjusted column widths ────────────────────────────
    cols_to_show = [wbs_col, milestone_col, plan_col, actual_col, remarks_col]
    valid_cols = [c for c in cols_to_show if c in df_display.columns]
    table_df = df_display[valid_cols]

    html = """
    <div style="overflow-x:auto; margin:20px 0;">
    <table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif; font-size:0.92rem;">
        <thead>
            <tr>
                <th style='background:#7c3aed; color:white; padding:10px 8px; text-align:left; font-weight:700; font-size:1.0rem; width:18%;'>WBS</th>
                <th style='background:#7c3aed; color:white; padding:10px 10px; text-align:left; font-weight:700; font-size:1.0rem; width:20%;'>Milestone</th>
                <th style='background:#7c3aed; color:white; padding:10px 8px; text-align:center; font-weight:700; font-size:1.0rem; width:10%;'>Plan Date</th>
                <th style='background:#7c3aed; color:white; padding:10px 8px; text-align:center; font-weight:700; font-size:1.0rem; width:10%;'>Actual Date</th>
                <th style='background:#7c3aed; color:white; padding:10px 12px; text-align:left; font-weight:700; font-size:1.0rem; width:35%;'>Remarks</th>
            </tr>
        </thead>
        <tbody>
    """

    prev_wbs = None
    for idx, row in table_df.iterrows():
        wbs_val = row[wbs_col]
        display_wbs = "" if wbs_val == prev_wbs else wbs_val
        prev_wbs = wbs_val

        # Light row coloring
        row_bg = "#f9fafb" if idx % 2 == 0 else "#ffffff"

        html += f"<tr style='background:{row_bg};'>"
        html += f"<td style='padding:8px 8px; border-bottom:1px solid #e5e7eb; font-weight:600;'>{display_wbs}</td>"
        html += f"<td style='padding:8px 10px; border-bottom:1px solid #e5e7eb; font-weight:500;'>{row[milestone_col]}</td>"
        html += f"<td style='padding:8px 8px; border-bottom:1px solid #e5e7eb; text-align:center; font-weight:500;'>{row.get(plan_col, '—')}</td>"
        html += f"<td style='padding:8px 8px; border-bottom:1px solid #e5e7eb; text-align:center; font-weight:500;'>{row.get(actual_col, '—')}</td>"
        html += f"<td style='padding:8px 12px; border-bottom:1px solid #e5e7eb; font-weight:400; opacity:0.9;'>{row.get(remarks_col, '—')}</td>"
        html += "</tr>"

    html += """
        </tbody>
    </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    # Sidebar (unchanged)
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
