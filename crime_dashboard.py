
import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set Matplotlib font to display Hebrew
rcParams['font.family'] = 'Arial'
rcParams['axes.unicode_minus'] = False  # Ensure minus signs display correctly

# Add custom CSS styling for RTL support
st.markdown(
    """
    <style>
    body {
        direction: rtl;
        text-align: right;
    }
    .css-18e3th9 {
        direction: rtl;
        text-align: right;
    }
    .css-1d391kg {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to load and process data
def load_data():
    urls = {
        "2020": "https://data.gov.il/api/3/action/datastore_search?resource_id=520597e3-6003-4247-9634-0ae85434b971",
        "2021": "https://data.gov.il/api/3/action/datastore_search?resource_id=3f71fd16-25b8-4cfe-8661-e6199db3eb12",
        "2022": "https://data.gov.il/api/3/action/datastore_search?resource_id=a59f3e9e-a7fe-4375-97d0-76cea68382c1",
        "2023": "https://data.gov.il/api/3/action/datastore_search?resource_id=32aacfc9-3524-4fba-a282-3af052380244",
        "2024": "https://data.gov.il/api/3/action/datastore_search?resource_id=5fc13c50-b6f3-4712-b831-a75e0f91a17e",
    }
    data_frames = []
    for year, url in urls.items():
        response = requests.get(url)
        data = response.json()
        records = data['result']['records']
        df = pd.DataFrame(records)
        df['Year'] = year  # Add a year column
        data_frames.append(df)
    return pd.concat(data_frames, ignore_index=True)

# Load the data
st.title("פשע בישראל (2020-2024)")
st.sidebar.header("אפשרויות סינון")
df_all = load_data()

# Convert "Year" to int and ensure proper handling of Hebrew text
df_all["Year"] = pd.to_numeric(df_all["Year"], errors="coerce")
df_all["StatisticGroup"] = df_all["StatisticGroup"].astype(str)

# Sidebar filter options
years = st.sidebar.multiselect("בחר שנים", sorted(df_all["Year"].unique()), default=sorted(df_all["Year"].unique()))
crime_types = st.sidebar.multiselect("בחר סוגי פשעים", df_all["StatisticGroup"].unique(), default=df_all["StatisticGroup"].unique())

# Filter the data based on user selection
filtered_data = df_all[(df_all["Year"].isin(years)) & (df_all["StatisticGroup"].isin(crime_types))]

# Visualization of crime trends
st.subheader("מגמות פשע לפי סוג")
if filtered_data.empty:
    st.write("אין נתונים זמינים עבור הבחירה.")
else:
    # Group and plot the data
    crime_counts = filtered_data.groupby(["Year", "StatisticGroup"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 6))
    crime_counts.plot(kind="bar", ax=ax, width=0.8)

    # Set Hebrew titles and labels
    ax.set_title("מגמות פשע לאורך השנים", fontsize=16, loc="center", horizontalalignment='center')
    ax.set_xlabel("שנה", fontsize=14)
    ax.set_ylabel("מספר הפשעים", fontsize=14)
    ax.legend(title="סוג פשע", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=12)
    plt.tight_layout()

    st.pyplot(fig)

# Display the filtered data
st.subheader("תצוגה מקדימה של נתונים מסוננים")
st.dataframe(filtered_data)
    