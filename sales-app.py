

import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Yuva's Sales Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #0b132b;
        background-image: url("https://images.unsplash.com/photo-1556741533-f6acd647d2fb");
        background-size: cover;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1C2541;
        color: white;
    }
    [data-testid="stSidebar"] .stSelectbox label, [data-testid="stSidebar"] .stMultiSelect label {
        font-size: 16px;
        color: #f0f0f0;
    }
    /* Titles */
    h1, h2, h3, h4 {
        color: #FF4B4B;
        font-family: "Segoe UI", sans-serif;
    }
    /* KPI Cards */
    .metric-card {
        padding: 20px;
        background: #1C2541;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
    }
    /* Hide footer/header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ------------------ HEADER / LOGO ------------------
st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)  # Logo
st.markdown("<h1 style='text-align: center;'>📊 Yuva's  Sales Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# ------------------ LOAD DATA ------------------
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io="supermarkt1_sales.xlsx",
        engine="openpyxl",
        sheet_name="Sales",
        skiprows=3,
        usecols="B:R",
        nrows=1000,
    )
    # Add 'hour' column to dataframe
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    return df

df = get_data_from_excel()

# ------------------ SIDEBAR FILTERS ------------------
st.sidebar.header("🔎 Please Filter Here:")
city = st.sidebar.multiselect(
    "🏙️ Select the City:",
    options=df["City"].unique(),
    default=[]  # nothing selected initially
)

customer_type = st.sidebar.multiselect(
    "🛍️ Select the Customer Type:",
    options=df["Customer_type"].unique(),
    default=[]  # nothing selected initially
)

gender = st.sidebar.multiselect(
    "👥 Select the Gender:",
    options=df["Gender"].unique(),
    default=[]  # nothing selected initially
)

df_selection = df.query(
    "City == @city & Customer_type ==@customer_type & Gender == @gender"
)

# Check if the dataframe is empty:
if df_selection.empty:
    st.warning("⚠️ No data available based on the current filter settings!")
    st.stop()

# ------------------ KPIs ------------------
total_sales = int(df_selection["Total"].sum())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = "⭐" * int(round(average_rating, 0))

average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='metric-card'><h3>Total Sales</h3><h2>US $ {total_sales:,}</h2></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><h3>Average Rating</h3><h2>{average_rating} {star_rating}</h2></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-card'><h3>Avg. Sale/Transaction</h3><h2>US $ {average_sale_by_transaction}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# ------------------ CHARTS ------------------
# SALES BY PRODUCT LINE
sales_by_product_line = df_selection.groupby(by=["Product line"])[["Total"]].sum().sort_values(by="Total")
fig_product_sales = px.bar(
    sales_by_product_line,
    x="Total",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Sales by Product Line</b>",
    color_discrete_sequence=["#FF4B4B"] * len(sales_by_product_line),
    template="plotly_dark",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# SALES BY HOUR
sales_by_hour = df_selection.groupby(by=["hour"])[["Total"]].sum()
fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Total",
    title="<b>Sales by Hour</b>",
    color_discrete_sequence=["#FF4B4B"] * len(sales_by_hour),
    template="plotly_dark",
)
fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

# Layout
left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)
