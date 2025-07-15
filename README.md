Portfolio Advisor App
A personalized portfolio analysis tool that takes your stock holdings, risk preferences, and investment goals — and returns data-driven insights, analysis, and stock suggestions, including outside recommendations based on market trends and news sentiment.

Features:
- Load your portfolio from CSV

- Fetch 6-month price history for each stock

- Fetch latest stock-related news

- Analyze short-term and long-term performance using LLMs 

- Suggest stocks outside your portfolio based on:
  *Risk Tolerance (Low/Medium/High)
  *Investment Horizon (Short/Medium/Long-term)
  *Investment Objective
  *Liquidity Needs


Built using LangGraph, OpenBB, Finnhub, and Streamlit


How It Works (Brief Overview)
-CSV Upload
 User uploads a CSV file with stock tickers.

-Graph Execution
 A LangGraph pipeline performs the following:
  *Loads the portfolio
  *Fetches price history (OpenBB)
  *Fetches news (Finnhub)
  *Analyzes the performance using LLMs
  *Suggests additional stocks based on preferences

-Result
 The output includes enriched stock data, sentiment-based suggestions, and personalized investment advice.

Setup Instructions:
 - Clone the repo:
     git clone https://github.com/vstejesh/stocks.git

 - Install dependencies(Preferably in a virtual env):
     pip install -r requirements.txt

 - Run the app:
     streamlit run app.py    
     


