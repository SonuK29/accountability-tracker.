import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Set page to wide mode and collapse sidebar for a cleaner look
st.set_page_config(page_title="Systemic Failure Tracker", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS FOR MINIMALIST, MASSIVE METRICS ---
st.markdown("""
    <style>
    .big-font {
        font-size: 75px !important;
        font-weight: 900;
        line-height: 1;
        color: #FF4B4B; /* Alert Red for Casualties */
        margin-bottom: 0px;
    }
    .big-font-dark {
        font-size: 75px !important;
        font-weight: 900;
        line-height: 1;
        color: #1f1f1f; /* Dark grey for Incidents */
        margin-bottom: 0px;
    }
    .label-font {
        font-size: 20px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
        margin-bottom: -10px;
    }
    /* Hide the default Streamlit main menu and footer for a cleaner app feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Header
st.title("Public Accountability Tracker")
st.markdown("Tracking systemic and infrastructure failures via daily news aggregation.", help="Data is automatically gathered daily from major news outlets.")

# Load Data
@st.cache_data(ttl=3600)
def load_data():
    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv")
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    else:
        return pd.DataFrame(columns=['Date', 'Category', 'Location', 'Casualties', 'Headline', 'Source_URL'])

df = load_data()

if df.empty:
    st.info("The database is currently empty. Waiting for the daily scraper to log the first incident.")
else:
    # ==========================================
    # 1. THE BOLD SUMMARY (Top Section)
    # ==========================================
    total_casualties = int(df['Casualties'].sum())
    total_incidents = len(df)
    
    st.markdown("<br>", unsafe_allow_html=True) # Spacer
    col1, col2, col3 = st.columns([1, 1, 1.5]) # Adjusted column widths
    
    with col1:
        st.markdown('<p class="label-font">Total Casualties</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font">{total_casualties}</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="label-font">Reported Incidents</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-font-dark">{total_incidents}</p>', unsafe_allow_html=True)

    with col3:
        most_frequent = df['Category'].mode()[0]
        st.markdown('<p class="label-font">Most Frequent Failure</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size: 35px; font-weight: 700; color: #1f1f1f; padding-top: 15px;">{most_frequent}</p>', unsafe_allow_html=True)

    st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

    # ==========================================
    # 2. MINIMAL INFOGRAPHICS (Middle Section)
    # ==========================================
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("**CASUALTIES BY CATEGORY**")
        category_df = df.groupby('Category')['Casualties'].sum().reset_index().sort_values(by='Casualties', ascending=True)
        
        # Horizontal bar chart with data labels written directly on the screen
        fig1 = px.bar(category_df, x='Casualties', y='Category', orientation='h', text='Casualties', color_discrete_sequence=['#FF4B4B'])
        fig1.update_traces(textposition='outside', textfont_size=16, textfont_weight='bold')
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, showticklabels=False, title=""), # Hide X axis completely
            yaxis=dict(title="", tickfont=dict(size=14, weight='bold')),
            margin=dict(l=0, r=40, t=10, b=0),
            height=350
        )
        # Disable the Plotly toolbar that appears on hover for a cleaner look
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

    with col_chart2:
        st.markdown("**INCIDENT TIMELINE**")
        timeline_df = df.groupby('Date')['Casualties'].sum().reset_index()
        
        # Area chart to show accumulation over time
        fig2 = px.area(timeline_df, x='Date', y='Casualties', markers=True, color_discrete_sequence=['#1f1f1f'])
