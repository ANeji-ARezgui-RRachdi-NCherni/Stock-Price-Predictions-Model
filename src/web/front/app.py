import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.environ["BACKEND_URL"]

st.title("📈 Stock Price Viewer")
companies = []
# List companies from FastAPI
try:
    companies = requests.get(f"{BACKEND_URL}/companies").json()
except Exception as e:
    st.error(f"Failed to load companies list: {e}")
    st.stop()

company = st.selectbox("Select a company", companies)

if company:
    with st.spinner(f"Loading stock data for {company}..."):
        response = requests.get(f"{BACKEND_URL}/stock/{company}")
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data["data"])
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)

            fig = px.line(df, x=df.index, y="cloture", title=f"Clôture Prices for {company}")
            fig.update_xaxes(rangeslider_visible=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"Error fetching stock data: {response.text}")

