import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Systemic Failure Tracker", layout="wide")
st.title("Public Accountability: Systemic Failure Tracker")
st.markdown("Tracking incidents linked to infrastructure and systemic failures via daily news aggregation.")

# 1. Load Data Securely
@st.cache_data(ttl=3600) # Caches data to load instantly for visitors
def load_data():
    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv")
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    else:
        return pd.DataFrame(columns=['Date', 'Category', 'Location', 'Casualties', 'Headline', 'Source_URL'])

df = load_data()

# 2. Display Dashboard
if df.empty:
    st.info("The database is currently empty. Waiting for the daily scraper to log the first incident.")
else:
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reported Incidents", len(df))
    col2.metric("Total Casualties Tracked", int(df['Casualties'].sum()))
    col3.metric("Most Frequent Issue", df['Category'].mode()[0])

    st.divider()

    # Visualizations
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.subheader("Casualties by Category")
        fig1 = px.bar(df.groupby('Category')['Casualties'].sum().reset_index(), 
                      x='Category', y='Casualties', color='Category')
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        st.subheader("Incident Timeline")
        fig2 = px.line(df.groupby('Date')['Casualties'].sum().reset_index(), 
                       x='Date', y='Casualties', markers=True)
        st.plotly_chart(fig2, use_container_width=True)

    # Raw Data Table
    st.subheader("Recent Incident Reports")
    st.dataframe(df.sort_values(by='Date', ascending=False), use_container_width=True)