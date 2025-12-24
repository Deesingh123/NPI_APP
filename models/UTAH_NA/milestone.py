import streamlit as st
import pandas as pd
from datetime import datetime

def main():
    # Back button to return to model selection
    if st.button("← Back to Dashboard", key="back_milestone"):
        if 'dashboard' in st.session_state:
            del st.session_state.dashboard
        st.rerun()

    #st.title("UTAH NA - Milestone Tracker Dashboard")

    REFRESH_INTERVAL = 30
    CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSERW8jK8wY8-01wqcDBtNY_g8Km2g3QyxNjT1BWIg2II95wvouLQ1wsgWckkY56Q/pub?gid=1960938483&single=true&output=csv"

    @st.cache_data(ttl=REFRESH_INTERVAL)
    def load_data():
        try:
            df = pd.read_csv(CSV_URL, header=None)
            df = df.iloc[1:]  # Skip header row
            df = df[[0, 1, 2, 3]]  # Keep only first 4 columns
            df.columns = ["Task", "Milestone_Type", "Plan_Date", "Actual_Date"]
            df = df.fillna("—")
            df = df.reset_index(drop=True)
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()

    df = load_data()

    # Beautiful Header (Green gradient like before)
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background:linear-gradient(135deg, #059669 0%, #10b981 100%); color:white; border-radius:16px; margin-bottom:30px; box-shadow: 0 12px 30px rgba(5,150,105,0.3);">
        <h1 style="margin:0; font-size:2.4rem; font-weight:800;">📋 Milestone Tracker Dashboard</h1>
        <p style="margin:10px 0 0 0; font-size:1.1rem;">
            Updated: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')} • Auto-refresh every {REFRESH_INTERVAL}s
        </p>
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

    # Metric Cards
    overdue_count = len(df[df['Status'].str.contains("Delayed|Overdue")])
    pending_count = len(df[df['Status'] == "Pending"])

    col_spacer1, col_overdue, col_spacer_mid, col_pending, col_spacer2 = st.columns([1.5, 5, 1, 5, 1.5])

    with col_overdue:
        st.markdown(f"""
        <div style="background:#ef4444; color:white; padding:20px 40px; border-radius:16px; text-align:center; box-shadow:0 10px 25px rgba(239,68,68,0.4);">
            <p style="margin:0; font-size:1.2rem; font-weight:700;">🔥 Overdue / Delayed</p>
            <h2 style="margin:10px 0 0 0; font-size:4.2rem; font-weight:900;">{overdue_count}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col_pending:
        st.markdown(f"""
        <div style="background:#fbbf24; color:black; padding:20px 40px; border-radius:16px; text-align:center; box-shadow:0 10px 25px rgba(251,191,36,0.4);">
            <p style="margin:0; font-size:1.2rem; font-weight:700;">⏳ Pending</p>
            <h2 style="margin:10px 0 0 0; font-size:4.2rem; font-weight:900;">{pending_count}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Filters
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        type_filter = st.selectbox("🔄 Filter by Milestone Type", ["All", "WBS", "Sub Milestone"], key="mil_type_utah")
    with fcol2:
        status_filter = st.selectbox("⚡ Filter by Status", ["All", "Overdue / Delayed", "Pending", "Completed On Time"], key="mil_status_utah")

    filtered = df.copy()
    if type_filter != "All":
        filtered = filtered[filtered["Milestone_Type"] == type_filter]
    if status_filter != "All":
        if status_filter == "Overdue / Delayed":
            filtered = filtered[filtered['Status'].str.contains("Delayed|Overdue")]
        elif status_filter == "Pending":
            filtered = filtered[filtered['Status'] == "Pending"]
        elif status_filter == "Completed On Time":
            filtered = filtered[filtered['Status'] == "Completed On Time"]

    # Alert
    if overdue_count > 0:
        st.error(f"🚨 URGENT: {overdue_count} milestones DELAYED or OVERDUE!")
    else:
        st.success("✅ All milestones are on track")

    # Beautiful HTML Table
    table_df = filtered[["Task", "Milestone_Type", "Plan_Date", "Actual_Date", "Status"]].copy()
    table_df['Plan_Date'] = table_df['Plan_Date'].dt.strftime('%d-%b').fillna("—")
    table_df['Actual_Date'] = table_df['Actual_Date'].dt.strftime('%d-%b').fillna("—")

    html = """
    <div style="overflow-x:auto; margin:20px 0;">
    <table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif;">
        <thead>
            <tr>
                <th style="background:#1e40af; color:white; padding:15px; text-align:left; font-weight:800;">Task</th>
                <th style="background:#1e40af; color:white; padding:15px; text-align:left; font-weight:800;">Milestone Type</th>
                <th style="background:#1e40af; color:white; padding:15px; text-align:left; font-weight:800;">Plan Date</th>
                <th style="background:#1e40af; color:white; padding:15px; text-align:left; font-weight:800;">Actual Date</th>
                <th style="background:#1e40af; color:white; padding:15px; text-align:left; font-weight:800;">Status</th>
            </tr>
        </thead>
        <tbody>
    """

    prev_task = None
    for _, row in table_df.iterrows():
        status = row['Status']
        status_style = ""
        if "Delayed" in status or "Overdue" in status:
            status_style = "background:#ef4444; color:white; font-weight:bold;"
        elif "On Time" in status:
            status_style = "background:#22c55e; color:white; font-weight:bold;"
        elif "Pending" in status:
            status_style = "background:#fbbf24; color:black; font-weight:bold;"

        display_task = "" if row['Task'] == prev_task else row['Task']
        prev_task = row['Task']

        html += "<tr>"
        html += f"<td style='padding:12px; border:1px solid #ddd;'>{display_task}</td>"
        html += f"<td style='padding:12px; border:1px solid #ddd;'>{row['Milestone_Type']}</td>"
        html += f"<td style='padding:12px; border:1px solid #ddd;'>{row['Plan_Date']}</td>"
        html += f"<td style='padding:12px; border:1px solid #ddd;'>{row['Actual_Date']}</td>"
        html += f"<td style='padding:12px; border:1px solid #ddd; {status_style}'>{row['Status']}</td>"
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
            "utah_na_milestone.csv",
            "text/csv"
        )

if __name__ == "__main__":
    main()