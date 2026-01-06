import streamlit as st
import pandas as pd
import gspread
from datetime import datetime



st.markdown("""
<style>
/* Page padding */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

/* Section card */
.card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    margin-bottom: 1.2rem;
}

/* Section title */
.section-title {
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Data editor tweaks */
[data-testid="stDataEditor"] {
    border-radius: 12px;
    overflow: hidden;
}

.stButton > button {
    background: white;
    color: #1f2937;
    border-radius: 12px;
    padding: 0.6rem 1.4rem;
    font-weight: 600;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    transition: all 0.2s ease-in-out;-[';/]
}

.stButton > button:hover {
    background: #f9fafb;
    border-color: #d1d5db;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}

/* Footer text */
.footer {
    text-align: center;
    color: #8a8a8a;
    font-size: 13px;
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)




def get_sheet():
    creds = dict(st.secrets["gcp_service_account"])
    creds["private_key"] = creds["private_key"].replace("\\n", "\n")

    gc = gspread.service_account_from_dict(creds)
    sh = gc.open_by_key("13sIsY5Cy1Pq-it9cX5WNPoz2RI76EjsnPJ73D4PKsag")
    return sh.worksheet("Daily_Issue_Tracking")


st.success("Connected to Google Sheet successfully ✅")


@st.cache_data(ttl=20)
def load_data():
    ws = get_sheet()
    df = pd.DataFrame(ws.get_all_records())

    if df.empty:
        return pd.DataFrame(columns=COLUMNS)

    # Convert date columns correctly
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    return df

# -------------------- SAVE DATA --------------------
def save_data(df):
    ws = get_sheet()

    # Convert dates back to string for Google Sheets
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype(str).replace("NaT", "")

    ws.clear()
    ws.update([df.columns.tolist()] + df.fillna("").values.tolist())

    st.cache_data.clear()

# -------------------- CONSTANTS --------------------
COLUMNS = [
    "Date",
    "Product",
    "Line / Area",
    "Issue Category",
    "Issue Description",
    "Impact",
    "Priority",
    "Responsible Owner",
    "Target Closure Date",
    "Action Planned",
    "Evening Status",
    "Actual Closure Date"
]

DATE_COLUMNS = [
    "Date",
    "Target Closure Date",
    "Actual Closure Date"
]


def main():
    st.markdown("<div class='section-title'>📋 Daily Issues Tracker</div>", unsafe_allow_html=True)

    df = load_data()

    if df.empty:
        df = pd.DataFrame(columns=COLUMNS)

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Date": st.column_config.DateColumn("Date"),
            "Target Closure Date": st.column_config.DateColumn("Target Closure Date"),
            "Actual Closure Date": st.column_config.DateColumn("Actual Closure Date"),
            "Priority": st.column_config.SelectboxColumn(
                "Priority",
                options=["High", "Medium", "Low"],
                default="Medium"
            ),
            "Impact": st.column_config.SelectboxColumn(
                "Impact",
                options=["Low", "Medium", "High"]
            ),
        }
    )

    if st.button("💾 Save Changes"):
        save_data(edited_df)
        st.success("Changes saved and synced with Google Sheet ✅")

    st.caption("Live sync with Google Sheets • Editable via Sheet or Dashboard")

# -------------------- RUN --------------------
if __name__ == "__main__":
    main()
