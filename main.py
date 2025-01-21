import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import io

#set page config
st.set_page_config(page_title="Crime Dashboard", layout="wide")

# Helper functions
@st.cache_data
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
        df['Year'] = int(year)  # Add year column
        df["Category"] = df["StatisticGroup"].apply(categorize_statistic_group)
        df = df.dropna(subset=["Category"])
        df["ReversedStatisticGroup"] = df["Category"].apply(lambda x: x[::-1])
        data_frames.append(df)
    return pd.concat(data_frames, ignore_index=True)

def categorize_statistic_group(stat_group):
    """
    Divides the statistic groups into 6
    :param stat_group: the initial statistic group
    :return: one of the 6 groups it belongs to
    """
    categories = {
        "עבירות פליליות כלליות": ['עבירות כלפי הרכוש', 'עבירות נגד גוף', 'עבירות נגד אדם', 'עבירות מין'],
        "עבירות מוסר וסדר ציבורי": ['עבירות כלפי המוסר', 'עבירות סדר ציבורי'],
        "עבירות ביטחון": ['עבירות בטחון'],
        "עבירות כלכליות ומנהליות": ['עבירות כלכליות', 'עבירות מנהליות', 'עבירות רשוי'],
        "עבירות תנועה": ['עבירות תנועה'],
        "עבירות מרמה": ['עבירות מרמה']
    }
    for category, types in categories.items():
        if stat_group in types:
            return category
    return None



# Streamlit layout
st.title("Crime Analysis Dashboard")

# side-bar navigation
menu_option = st.sidebar.radio("Select Visualization:", ["Overview", "Heatmap", "October 7th"])

if menu_option == 'Overview':
    df = load_data()
    # OVERVIEW VISUALIZATION
    # Determine Y-axis max value before filtering
    years = ["All Years (mean)"] + sorted(df["Year"].dropna().unique().astype(int).tolist())
    # Sidebar filters
    year_selected = st.selectbox("Select Year:", years, index=0)
    st.markdown("""
        <style>
        .stSelectbox [data-baseweb="select"] {
            width: 200px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    split_by_quarter = st.checkbox("Split by Quarter")

    # Filter data based on selected year
    unique_categories = df["ReversedStatisticGroup"].drop_duplicates().tolist()
    if year_selected == "All Years (mean)":
        filtered_data = df
        crime_counts = (
            filtered_data.groupby("ReversedStatisticGroup").size() / len(filtered_data["Year"].unique())
        ).reindex(unique_categories, fill_value=0)
    else:
        filtered_data = df[df["Year"] == int(year_selected)]
        crime_counts = filtered_data["ReversedStatisticGroup"].value_counts().reindex(unique_categories, fill_value=0)

    # Generate plot
    fig, ax = plt.subplots(figsize=(10, 6))
    if split_by_quarter:
        if year_selected == "All Years (mean)":
            # Calculate mean for all years grouped by category and quarter
            grouped_data = (
                filtered_data.groupby(["ReversedStatisticGroup", "Quarter", "Year"])  # Include "Year" to count per year
                .size()
                .reset_index(name="Counts")  # Reset index to include 'Quarter' and 'Year'
                .groupby(["ReversedStatisticGroup", "Quarter"])[
                    "Counts"]  # Group by 'ReversedStatisticGroup' and 'Quarter'
                .mean()  # Calculate the mean across years
                .reset_index()  # Reset index to keep 'ReversedStatisticGroup' and 'Quarter'
            )

        else:
            # Group data for the selected year
            grouped_data = (
                filtered_data.groupby(["ReversedStatisticGroup", "Quarter"])
                .size()
                .reset_index(name="Counts")
            )
        sns.barplot(
            data=grouped_data,
            x="ReversedStatisticGroup",
            y="Counts",
            hue="Quarter",
            palette=['#9CFFFA', '#6153CC', '#FFED65', '#F96E46'],
            ax=ax
        )
        ax.set_title("גוסו ןועבר יפל םיעשפה רפסמ", fontsize=16)
        ax.set_xlabel("עשפה גוס", fontsize=14)
        ax.set_ylabel("ןועבר", fontsize=14)
    else:
        crime_counts.plot(kind="bar", ax=ax, color="#F96E46")
        ax.set_title("גוס יפל םיעשפה רפסמ", fontsize=16)
        ax.set_xlabel("עשפה גוס", fontsize=14)
        ax.set_ylabel("םיעשפה רפסמ", fontsize=14)
        ax.tick_params(axis="x", labelrotation=45)
        ax.set_ylim(0, 18000)

    plt.tight_layout()

    # Display plot
    st.pyplot(fig)
