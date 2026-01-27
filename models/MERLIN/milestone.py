import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSe4nuvqUK1UQdv7o0aC8sunzc3sIIA6Ml29g9FV2-4CBO254JwHhA7HXXEDzefSqkgDxXNuc9bXp4-/pub?gid=1944217723&single=true&output=csv"

    @st.cache_data(ttl=REFRESH_INTERVAL)
    def load_data():
        try:
            df = pd.read_csv(CSV_URL, header=None)
            df = df.iloc[1:]  # Skip header row
            df = df.iloc[:, :5]   # first 5 columns
            df.columns = ["Sub-Milestones", "Plan_Date", "Actual_Date", "Lead Time", "Remarks"]
            df = df.fillna("—")
            df = df.reset_index(drop=True)
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()

    df = load_data()

    # Slightly more compact header
    st.markdown(f"""
    <div style="text-align:center; padding:16px; background:linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%); color:white; border-radius:12px; margin-bottom:12px;">
        <h1 style="margin:0; font-size:2.4rem; color:white; font-weight:800;">Merlin Milestone</h1>
        <p style="margin:8px 0 0 0; font-size:1rem;">
            Updated: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')} • refresh every {REFRESH_INTERVAL}s
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Compact timeline
    st.markdown("""
    <div style="background:#f0f9ff; padding:15px; border-radius:20px; margin:15px 0; box-shadow:0 8px 30px rgba(0,0,0,0.1); border:1px solid #bae6fd;">
        <div style="text-align:center;">
            <h3 style="color:#0c4a6e; font-size:1.8rem; margin:0 0 15px 0; font-weight:700;"> Timelines </h3>
            <div style="display:flex; justify-content:center; gap:80px; flex-wrap:wrap;">
                <div style="text-align:center;">
                    <p style="font-size:1.5rem; font-weight:bold; color:#166534; margin:0;">PVT</p>
                    <p style="font-size:1.3rem; color:#0c4a6e; margin:8px 0 0 0;">16 JAN</p>
                </div>
                <div style="text-align:center;">
                    <p style="font-size:1.5rem; font-weight:bold; color:#0c4a6e; margin:0;">OK2P</p>
                    <p style="font-size:1.3rem; color:#0c4a6e; margin:8px 0 0 0;">23 FEB</p>
                </div>
                <div style="text-align:center;">
                    <p style="font-size:1.5rem; font-weight:bold; color:#0c4a6e; margin:0;">OK2R</p>
                    <p style="font-size:1.3rem; color:#0c4a6e; margin:8px 0 0 0;">16 APR</p>
                </div>
                <div style="text-align:center;">
                    <p style="font-size:1.5rem; font-weight:bold; color:#0c4a6e; margin:0;">OK2S</p>
                    <p style="font-size:1.3rem; color:#0c4a6e; margin:8px 0 0 0;">06 MAR</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Date parsing
    current_year = datetime.now().year
    def parse_date(val):
        if pd.isna(val) or val == "—":
            return pd.NaT
        s = str(val).strip()
        if '-' in s and len(s.split('-')) == 2:
            s += f"-{current_year}"
        return pd.to_datetime(s, dayfirst=True, errors='coerce')

    df['Plan_Date']  = df['Plan_Date'].apply(parse_date)
    df['Actual_Date'] = df['Actual_Date'].apply(parse_date)
    today = pd.Timestamp.today().normalize()

    # Status (used for light row coloring)
    def get_status(row):
        if pd.notna(row['Actual_Date']):
            return "Done" if row['Actual_Date'] <= row['Plan_Date'] else "Delayed"
        elif pd.notna(row['Plan_Date']) and row['Plan_Date'] < today:
            return "Overdue"
        return "Pending"

    df['Status'] = df.apply(get_status, axis=1)

    # Prepare display data
    table_df = df.copy()
    table_df['Plan_Date']  = table_df['Plan_Date'].dt.strftime('%d-%b-%y').fillna("—")
    table_df['Actual_Date'] = table_df['Actual_Date'].dt.strftime('%d-%b-%y').fillna("—")

    # ── Slightly more compact table ─────────────────────────────────────────
    html = """
    <div style="overflow-x:auto; margin:12px 0;">
    <table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif; font-size:0.94rem;">
        <thead>
            <tr style="background:#1e40af; color:white;">
                <th style="padding:10px 10px; text-align:left; font-weight:700; width:24%;">Sub-Milestones</th>
                <th style="padding:10px 8px; text-align:center; font-weight:700; width:14%;">Plan Date</th>
                <th style="padding:10px 8px; text-align:center; font-weight:700; width:14%;">Actual Date</th>
                <th style="padding:10px 8px; text-align:center; font-weight:700; width:10%;">Lead Time</th>
                <th style="padding:10px 10px; text-align:left;   font-weight:700; width:38%;">Remarks</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in table_df.iterrows():
        status = row.get('Status', 'Pending')
        row_bg = ""
        if status == "Done":
            row_bg = "background:#f0fdf4;"
        elif status in ["Overdue", "Delayed"]:
            row_bg = "background:#fef2f2;"

        html += f"<tr style='{row_bg}'>"
        html += f"<td style='padding:8px 10px; border:1px solid #e5e7eb;'>{row['Sub-Milestones']}</td>"
        html += f"<td style='padding:8px 8px; border:1px solid #e5e7eb; text-align:center;'>{row['Plan_Date']}</td>"
        html += f"<td style='padding:8px 8px; border:1px solid #e5e7eb; text-align:center;'>{row['Actual_Date']}</td>"
        html += f"<td style='padding:8px 8px; border:1px solid #e5e7eb; text-align:center;'>{row['Lead Time']}</td>"
        html += f"<td style='padding:8px 10px; border:1px solid #e5e7eb;'>{row['Remarks']}</td>"
        html += "</tr>"

    html += """
        </tbody>
    </table>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.success("🎯 MERLIN")
        st.download_button(
            "📥 Download CSV",
            table_df.to_csv(index=False).encode(),
            "merlin_milestone.csv",
            "text/csv"
        )

if __name__ == "__main__":
    main()
