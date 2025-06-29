import streamlit as st

# Set page configuration
st.set_page_config(page_title="Portfolio Advicer", layout="centered")

# App title
st.title("Portfolio Advicer")

# Instructions
st.write("Upload a CSV of your portfolilo to get personalized advice.")

risk_tolerance = st.selectbox("Select your risk tolerance:", ["Low", "Medium", "High"])
investment_horizon = st.selectbox("Select your investment duration:", ["Short-term", "Medium-term", "Long-term"])


# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "txt"])

# Optional: show file content
if uploaded_file is not None:
    st.write("📂 File uploaded successfully!")

    # Example: read and display contents based on file type
    if uploaded_file.name.endswith(".txt"):
        content = uploaded_file.read().decode("utf-8")
        st.text_area("📄 File Content", content, height=200)
    elif uploaded_file.name.endswith(".csv"):
        import pandas as pd
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

    # Example logic: loop through content
    st.write("🚀 Generating advice for file contents...")
    # TODO: connect to your stock analysis logic

