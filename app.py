

import streamlit as st
import pandas as pd
import tempfile
from graph_builder import graph  # import your compiled graph

# --- Streamlit UI ---
st.set_page_config(page_title="Portfolio Advicer", layout="centered")
st.title("📈 Portfolio Advicer")
st.write("Upload a CSV of your portfolio to get personalized financial insights.")

# User Inputs
risk_tolerance = st.selectbox("Select your risk tolerance:", ["Low", "Medium", "High"])
investment_horizon = st.selectbox("Select your investment horizon:", ["Short-term", "Medium-term", "Long-term"])
# --- Investment Objective ---
st.subheader(" Investment Objective")
objective_options = ["Growth", "Income", "Capital Preservation", "Speculation", "Other"]
selected_objective = st.selectbox("What is your primary investment goal?", objective_options)

if selected_objective == "Other":
    custom_objective = st.text_input("Please specify your investment objective:")
    investment_objective = custom_objective
else:
    investment_objective = selected_objective

# --- Liquidity Needs ---
# st.subheader("Liquidity Needs")
liquidity_option = st.selectbox(
    "When do you expect to need this capital?",
    ["< 6 months", "6–12 months", "1–3 years", "3–5 years", "More than 5 years"]
)
# Map to backend-friendly format if needed
liquidity_needs = liquidity_option

uploaded_file = st.file_uploader("Upload your portfolio CSV", type=["csv"])

# --- Main Logic ---
if uploaded_file:
    st.success("📂 File uploaded successfully!")
    df = pd.read_csv(uploaded_file)
    st.write("🔍 Uploaded Portfolio Preview")
    st.dataframe(df)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        df.to_csv(tmp.name, index=False)
        csv_path = tmp.name

    if st.button("Run Portfolio Analysis"):
        st.info("⏳ Running analysis...")
        state = {
            "user_uploaded_file": csv_path,
            "risk_tolerance": risk_tolerance,
            "investment_horizon": investment_horizon,
            "objective": investment_objective,
            "liquidity_needs": liquidity_needs,
            "portfolio": [],
            "summary": [],
            "final_response": [],
            "messages": []
        }

        result = graph.invoke(state)

        st.success("✅ Analysis complete!")
        
        for stock in result["portfolio"]:
            st.subheader(f"📊 {stock['ticker']}")
            
            with st.expander("📈 Price History"):
                st.dataframe(stock["prices"].tail())

            with st.expander("📰 Recent News"):
                st.dataframe(stock["news"].head())

            with st.expander("🧠 AI Summary"):
                st.markdown(stock.get("recommendation", "No analysis available."))

        st.subheader("🧾 Summary")
        st.write(result.get("summary", "No summary generated."))
