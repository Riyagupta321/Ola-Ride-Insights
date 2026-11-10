import os
import glob
import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Ola Ride Insights", page_icon="🚖", layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "OLA_Cleaned.csv")
IMAGES_DIR = os.path.join(BASE_DIR, "app", "images")


@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)


@st.cache_resource
def get_connection():
    # Load the CSV into an in-memory SQLite database so SQL queries can run on it
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    load_data().to_sql("ola_rides", conn, index=False, if_exists="replace")
    return conn


QUERIES = {
    "Q1: All successful bookings": """
SELECT *
FROM ola_rides
WHERE Booking_Status = 'Success'
""",
    "Q2: Average ride distance per vehicle type": """
SELECT Vehicle_Type,
       ROUND(AVG(Ride_Distance), 2) AS Avg_Ride_Distance
FROM ola_rides
WHERE Booking_Status = 'Success'
GROUP BY Vehicle_Type
ORDER BY Avg_Ride_Distance DESC
""",
    "Q3: Total rides cancelled by customers": """
SELECT COUNT(*) AS Total_Cancelled_By_Customers
FROM ola_rides
WHERE Booking_Status = 'Canceled by Customer'
""",
    "Q4: Top 5 customers by number of rides": """
SELECT Customer_ID,
       COUNT(Booking_ID) AS Total_Rides
FROM ola_rides
GROUP BY Customer_ID
ORDER BY Total_Rides DESC
LIMIT 5
""",
    "Q5: Driver cancellations (personal and car related issues)": """
SELECT COUNT(*) AS Driver_Cancellations_Personal_Car_Issue
FROM ola_rides
WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue'
""",
    "Q6: Max and min driver ratings for Prime Sedan": """
SELECT MAX(Driver_Ratings) AS Max_Driver_Rating,
       MIN(Driver_Ratings) AS Min_Driver_Rating
FROM ola_rides
WHERE Vehicle_Type = 'Prime Sedan'
""",
    "Q7: Rides paid using UPI": """
SELECT *
FROM ola_rides
WHERE Payment_Method = 'UPI'
""",
    "Q8: Average customer rating per vehicle type": """
SELECT Vehicle_Type,
       ROUND(AVG(Customer_Rating), 2) AS Avg_Customer_Rating
FROM ola_rides
GROUP BY Vehicle_Type
ORDER BY Avg_Customer_Rating DESC
""",
    "Q9: Total booking value of successful rides": """
SELECT SUM(Booking_Value) AS Total_Booking_Value
FROM ola_rides
WHERE Booking_Status = 'Success'
""",
    "Q10: Incomplete rides with reason": """
SELECT Booking_ID,
       Incomplete_Rides_Reason
FROM ola_rides
WHERE Incomplete_Rides = 'Yes'
""",
}

df = load_data()
conn = get_connection()

st.sidebar.title("🚖 Ola Ride Insights")
page = st.sidebar.radio(
    "Go to", ["Home", "SQL Insights", "Data Explorer", "Dashboard"]
)

# ---------------- Home ----------------
if page == "Home":
    st.title("Ola Ride Insights")
    st.write(
        "Ride-sharing analytics for July 2024: SQL insights, an interactive "
        "data explorer and the Power BI dashboard."
    )

    success = df[df["Booking_Status"] == "Success"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Bookings", f"{len(df):,}")
    col2.metric("Successful Rides", f"{len(success):,}")
    col3.metric("Success Rate", f"{len(success) / len(df):.2%}")
    col4.metric("Total Revenue", f"₹{success['Booking_Value'].sum():,}")

    st.subheader("Booking status breakdown")
    st.bar_chart(df["Booking_Status"].value_counts())

# ---------------- SQL Insights ----------------
elif page == "SQL Insights":
    st.title("SQL Insights")
    choice = st.selectbox("Select a query", list(QUERIES.keys()))
    sql = QUERIES[choice].strip()
    st.code(sql, language="sql")

    result = pd.read_sql_query(sql, conn)
    st.write(f"Rows returned: {len(result):,}")
    st.dataframe(result.head(1000), use_container_width=True)

# ---------------- Data Explorer ----------------
elif page == "Data Explorer":
    st.title("Data Explorer")

    vehicles = st.sidebar.multiselect(
        "Vehicle type", sorted(df["Vehicle_Type"].unique())
    )
    statuses = st.sidebar.multiselect(
        "Booking status", sorted(df["Booking_Status"].unique())
    )
    customer = st.sidebar.text_input("Search Customer ID (e.g. CID713523)")

    filtered = df.copy()
    if vehicles:
        filtered = filtered[filtered["Vehicle_Type"].isin(vehicles)]
    if statuses:
        filtered = filtered[filtered["Booking_Status"].isin(statuses)]
    if customer:
        filtered = filtered[
            filtered["Customer_ID"].str.contains(customer, case=False, na=False)
        ]

    st.write(f"Rows matching filters: {len(filtered):,}")
    st.dataframe(filtered.head(1000), use_container_width=True)

# ---------------- Dashboard ----------------
elif page == "Dashboard":
    st.title("Power BI Dashboard")
    images = sorted(glob.glob(os.path.join(IMAGES_DIR, "page_*.png")))
    if not images:
        st.warning("No dashboard images found in app/images.")
    for img in images:
        st.image(img, use_container_width=True)