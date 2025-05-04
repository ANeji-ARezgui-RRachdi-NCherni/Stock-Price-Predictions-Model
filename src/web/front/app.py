import os
from dotenv import load_dotenv
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Load environment variables
load_dotenv()
BACKEND_URL = os.environ.get("BACKEND_URL")

# Streamlit config
st.set_page_config(page_title="StockWise", page_icon="📈", layout="wide")

# Define navigation pages
PAGES = ["Home", "Data & Predict", "News & Insights", "Chatbot"]
params = st.query_params
current_page = params.get("page", "Home")
if current_page not in PAGES:
    current_page = "Home"

# --- Apply header styling ---
st.markdown("""
<style>
/* Blue bar styling applied directly to horizontal block */
div[data-testid="stHorizontalBlock"] {
    background-color: #0a1f44;
    padding: 1rem 2rem;
    border-bottom: 2px solid #1b263b;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.top-logo {
    font-size: 1.8rem;
    font-weight: 700;
    font-family: 'Segoe UI', sans-serif;
    color: white;
    display: flex;
    align-items: center;
}
.top-logo img {
    height: 30px;
    margin-right: 0.5rem;
}
.stButton > button {
    background-color: #415a77;
    color: white;
    border: none;
    padding: 0.45rem 1.1rem;
    border-radius: 20px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s ease;
}
.stButton > button:hover {
    background-color: #577590;
}
</style>
""", unsafe_allow_html=True)

# --- Render top bar (logo + nav buttons) in one row ---
logo_col, *nav_cols = st.columns([2, 1, 1, 1, 1])
with logo_col:
    st.markdown("""
    <div class="top-logo">
        <img src="https://cdn-icons-png.flaticon.com/512/2721/2721290.png" alt="logo">
        StockWise
    </div>
    """, unsafe_allow_html=True)

for col, page in zip(nav_cols, PAGES):
    with col:
        if st.button(page, key=f"nav-{page}"):
            st.query_params["page"] = page
            st.rerun()

# --- Main content ---
with st.spinner(f"Loading {current_page}..."):
    if current_page == "Home":
        st.header("Welcome to StockWise 📊")
        st.write("Your companion for stock insights and AI-powered forecasts.")
        st.subheader("💡 Quick Tips")
        for tip in [
            "📈 Make informed decisions with data.",
            "🛡️ Diversify to manage risk.",
            "⏳ Invest early to harness growth.",
            "🧘 Focus on long-term goals."
        ]:
            st.success(tip)

    elif current_page == "Data & Predict":
        st.header("📉 Historical & Predicted Stock Prices")
        try:
            companies = requests.get(f"{BACKEND_URL}/companies").json()
        except Exception:
            st.error("❌ Could not fetch company list.")
            st.stop()
        company = st.selectbox("Select a company", companies)
        if company:
            with st.spinner("Fetching data..."):
                res = requests.get(f"{BACKEND_URL}/stock/{company}")
                df = pd.DataFrame(res.json()["data"])
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
                df_pred = df.tail(5).copy()
                df_pred.index = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=5)
                df_pred["cloture"] = df["cloture"].iloc[-1] * (1 + pd.Series([0.01, -0.005, 0.008, 0.002, -0.003]))
                fig = px.line(title=f"{company}: Actual vs Predicted")
                fig.add_scatter(x=df.index, y=df["cloture"], mode="lines", name="Actual")
                fig.add_scatter(x=df_pred.index, y=df_pred["cloture"], mode="lines", name="Predicted", line=dict(dash="dash"))
                fig.update_xaxes(rangeslider_visible=True)
                st.plotly_chart(fig, use_container_width=True)

    elif current_page == "News & Insights":
        st.header("📰 Market News & Recommendations")
        st.info("Coming soon — stay tuned!")

    elif current_page == "Chatbot":
        st.header("💬 AI Chat Assistant")
        st.warning("Under development — check back soon!")

# --- Hide footer ---
st.markdown('<style>footer {visibility: hidden;}</style>', unsafe_allow_html=True)
