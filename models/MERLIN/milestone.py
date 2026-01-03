import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    # Back button to return to model selection
    #if st.button("← Back to Dashboard", key="back_milestone"):
     #   if 'dashboard' in st.session_state:
      #      del st.session_state.dashboard
       # st.rerun()

    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSe4nuvqUK1UQdv7o0aC8sunzc3sIIA6Ml29g9FV2-4CBO254JwHhA7HXXEDzefSqkgDxXNuc9bXp4-/pub?gid=1944217723&single=true&output=csv"

    @st.cache_data(ttl=REFRESH_INTERVAL)
    def load_data():
        try:
            df = pd.read_csv(CSV_URL, header=None)
            df = df.iloc[1:]  # Skip header row
            df = df[[0, 1, 2, 3, 4]]  # Keep only first 5 columns
            df.columns = ["Sub-Milestones", "Plan_Date", "Actual_Date", "Lead Time", "Remarks"]  # Rename columns
            df = df.fillna("—")
            df = df.reset_index(drop=True)
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()

    df = load_data()

    # Beautiful Header
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background:linear-gradient(135deg, #059669 0%, #10b981 100%); color:white; border-radius:16px; margin-bottom:15px; box-shadow: 0 12px 30px rgba(5,150,105,0.3);">
        <h1 style="margin:0; font-size:2.4rem; color:white; font-weight:800;">📋 MERLIN Milestone</h1>
        <p style="margin:10px 0 0 0; font-size:1.1rem;">
            Updated: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')} • Auto-refresh every {REFRESH_INTERVAL}s
        </p>
    </div>
    """, unsafe_allow_html=True)

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

    # Status calculation
    current_year = datetime.now().year

    def parse_date(val):
        if pd.isna(val) or val == "—":
            return pd.NaT
        s = str(val).strip()
        if '-' in s and len(s.split('-')) == 2:
            s = s + f"-{current_year}"
        return pd.to_datetime(s, dayfirst=True, errors='coerce')

    df['Plan_Date'] = df['Plan_Date'].apply(parse_date)
    df['Actual_Date'] = df['Actual_Date'].apply(parse_date)
    today = pd.Timestamp.today().normalize()

    def get_status(row):
        if pd.notna(row['Actual_Date']):
            return "Completed On Time" if pd.notna(row['Plan_Date']) and row['Actual_Date'] <= row['Plan_Date'] else "Delayed"
        elif pd.notna(row['Plan_Date']) and row['Plan_Date'] < today:
            return "Overdue (No Actual)"
        else:
            return "Pending"

    df['Status'] = df.apply(get_status, axis=1)

    # Filters (optional - you can add if needed)
    filtered = df.copy()

    # Beautiful HTML Table
    table_df = filtered[["Sub-Milestones", "Plan_Date", "Actual_Date", "Lead Time", "Remarks"]].copy()
    table_df['Plan_Date'] = table_df['Plan_Date'].dt.strftime('%d-%b-%y').fillna("—")
    table_df['Actual_Date'] = table_df['Actual_Date'].dt.strftime('%d-%b-%y').fillna("—")

    html = """
    <div style="overflow-x:auto; margin:15px 0;">
    <table style="width:95%; border-collapse:collapse; font-family:Arial, sans-serif; text-align:left; margin:auto;">
        <thead>
            <tr>
                <th style="background:#1e40af; color:white; padding:15px; text-align:left; font-weight:800;">Sub-Milestones</th>
                <th style="background:#1e40af; color:white; padding:15px; text-align:left; font-weight:800;">Plan Date</th>
                <th style="background:#1e40af; color:white; padding:15px; text-align:left; font-weight:800;">Actual Date</th>
                <th style="background:#1e40af; color:white; padding:15px; text-align:left; font-weight:800;">Lead Time</th>
                <th style="background:#1e40af; color:white; padding:15px; text-align:left; font-weight:800;">Remarks</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in table_df.iterrows():
        html += "<tr>"
        html += f"<td style='padding:12px; border:1px solid #ddd; font-size:1.0rem;'>{row['Sub-Milestones']}</td>"
        html += f"<td style='padding:12px; border:1px solid #ddd; font-size:1.0rem;'>{row['Plan_Date']}</td>"
        html += f"<td style='padding:12px; border:1px solid #ddd; font-size:1.0rem;'>{row['Actual_Date']}</td>"
        html += f"<td style='padding:12px; border:1px solid #ddd; font-size:1.0rem;'>{row['Lead Time']}</td>"
        html += f"<td style='padding:12px; border:1px solid #ddd; font-size:1.0rem;'>{row['Remarks']}</td>"
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
            "📥 Download Current View",
            table_df.to_csv(index=False).encode(),
            "merlin_milestone.csv",
            "text/csv"
        )

if __name__ == "__main__":
    main()

