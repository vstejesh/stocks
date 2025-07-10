from typing import cast
from state import StockInfo, AppState
import time
import pandas as pd
import datetime as dt
import finnhub
from dotenv import load_dotenv
from utils import (
    get_price_history, 
    get_news,
    get_price_analysis,
    get_news_analysis,
    get_stock_advice    
)
import os
from langchain_core.messages import AnyMessage  # if you're using LangGraph
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

llm = ChatGroq(
    temperature=0.35,
    model_name="llama-3.1-8b-instant",
    api_key=os.environ.get("GROQ_API_KEY"),
)


# Initialize the Finnhub client
load_dotenv()
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY")) 


def load_portfolio(state: AppState) -> dict:
    import pandas as pd
    from datetime import datetime

    file_path = state.get("user_uploaded_file")
    df = pd.read_csv(file_path)

    portfolio = []
    for _, row in df.iterrows():
        stock = StockInfo(
            ticker=row["Ticker"],
            shares_held=row["Shares Held"],
            buy_price=row["Buy Price"],
            current_price=row["Current Price"],
            sector=row["Sector"],
            purchase_date=row["Purchase Date"],
            prices=pd.DataFrame(),  # placeholder
            news=pd.DataFrame(),    # placeholder
            price_analyst_report="",
            news_analyst_report="",
            recommendation=""
        )
        portfolio.append(stock)

    return {"portfolio": portfolio}


def price_history_node(state: AppState) -> dict:
    start_date = (dt.datetime.now() - dt.timedelta(days=180)).strftime("%Y-%m-%d")
    end_date = dt.datetime.now().strftime("%Y-%m-%d")

    updated_portfolio = []

    for stock in state["portfolio"]:
        ticker = stock["ticker"]
        print(f"\nFetching price history for: {ticker} from {start_date} to {end_date}")
        try:
            price_df = get_price_history(ticker, start=start_date, end=end_date)
            print(f"{ticker} — rows fetched: {len(price_df)}")
            stock["prices"] = price_df
            # print(price_df.head(2))
        except Exception as e:
            print(f"Error fetching price history for {ticker} - {e}")
            stock["prices"] = pd.DataFrame()  # fallback
        updated_portfolio.append(stock)

    return {"portfolio": updated_portfolio}



def news_fetch_node(state: AppState) -> dict:
    updated_portfolio = []

    for stock in state["portfolio"]:
        ticker = stock["ticker"]
        try:

            news_df = get_news(ticker)
            stock["news"] = news_df
            print(f"Fetching news for: {ticker}")
            # print(news_df.head())
        except Exception as e:
            stock["news"] = pd.DataFrame()  # fallback
        updated_portfolio.append(stock)

    return {"portfolio": updated_portfolio}


def price_analysis_node(state: AppState) -> dict:
    updated_portfolio = []

    for stock in state["portfolio"]:
        ticker = stock["ticker"]
        print(f"\nAnalyzing price data for: {ticker}")
        if stock["prices"].empty:
            stock["price_analyst_report"] = "No price data available"
            updated_portfolio.append(stock)
            print("erroor")
            continue
        try:
            # Simulate a price analysis report
            report= get_price_analysis(ticker, stock["prices"])
            print("log test")
            stock["price_analyst_report"] = report
            print(f"Price analysis for {ticker} completed successfully.")
        except Exception as e:
            stock["price_analyst_report"] = f"Error in price analysis for {ticker} - {e}"
        updated_portfolio.append(stock)
        
    return {"portfolio": updated_portfolio}    

def news_analysis_node(state: AppState) -> dict:
    updated_portfolio = []

    for stock in state["portfolio"]:
        ticker = stock["ticker"]
        if stock["news"].empty:
            stock["news_analyst_report"] = "No news data available"
            updated_portfolio.append(stock)
            continue
        try:
            news_report = get_news_analysis(ticker, stock["news"])
            stock["news_analyst_report"] = news_report
            print(f"News analysis for {ticker} completed successfully.")
        except Exception as e:
            stock["news_analyst_report"] = f"Error in news analysis for {ticker} - {e}"
        updated_portfolio.append(stock)

    return {"portfolio": updated_portfolio}

def stock_advice_node(state: AppState) -> dict:
    updated_portfolio = []

    for stock in state["portfolio"]:
        ticker = stock["ticker"]
        try:
            # Simulate a stock advice report
            risk_tolerance = state["risk_tolerance"]
            horizon = state["investment_horizon"]
            objective = state.get("objective", "Balanced")
            liquidity_needs = state.get("liquidity_needs", "Medium")
            recommendation = get_stock_advice(ticker, stock["price_analyst_report"], stock["news_analyst_report"], risk_tolerance, horizon, objective, liquidity_needs)
            stock["recommendation"] = recommendation
            print(f"Advice for {ticker}: {recommendation}")
        except Exception as e:
            stock["recommendation"] = f"Error generating advice for {ticker} - {e}"
        updated_portfolio.append(stock)

    return {"portfolio": updated_portfolio}

def summarize_node(state: AppState) -> dict:
    updated_summary= {}

    portfolio = state["portfolio"]
    risk_tolerance = state["risk_tolerance"]
    horizon = state["investment_horizon"]
    objective = state.get("objective", "Balanced")
    liquidity_needs = state.get("liquidity_needs", "Medium")

    total_investment = sum(stock["shares_held"] * stock["buy_price"] for stock in portfolio)
    current_value = sum(stock["shares_held"] * stock["current_price"] for stock in portfolio)
    profit_loss = current_value - total_investment
    profit_loss_percent = (profit_loss / total_investment * 100) if total_investment else 0.0

    # Diversification
    sector_totals = {}
    for stock in portfolio:
        sector = stock["sector"]
        stock_value = stock["shares_held"] * stock["current_price"]
        sector_totals[sector] = sector_totals.get(sector, 0.0) + stock_value

    diversification = {
        sector: round((value / current_value) * 100, 2) for sector, value in sector_totals.items()
    }

    # Risk Score (simple volatility measure)
    returns = [
        (stock["current_price"] - stock["buy_price"]) / stock["buy_price"]
        for stock in portfolio if stock["buy_price"] > 0
    ]
    risk_score = round((pd.Series(returns).std() or 0.0) * 100, 2)

    # Format individual stock advice snippets
    stock_summaries = []
    for stock in portfolio:
        entry = f"""🔹 **{stock['ticker']}** ({stock['sector']})
        - Buy Price: ₹{stock['buy_price']}
        - Current Price: ₹{stock['current_price']}
        - Shares: {stock['shares_held']}
        - Stock Advice: {stock.get('recommendation', 'N/A')}
        """
        stock_summaries.append(entry)
    stock_summary_text = "\n\n".join(stock_summaries)

    prompt= PromptTemplate(
        template="""
        You are a financial assistant summarizing an entire investment portfolio based on the following data:

        Risk Tolerance: {risk_tolerance}
        Investment Horizon: {horizon}
        Objective: {objective}
        Liquidity Needs: {liquidity_needs}
        Total Investment: ₹{total_investment}
        Current Value: ₹{current_value}
        Profit/Loss: ₹{profit_loss} ({profit_loss_percent:.2f}%)
        Diversification: {diversification}
        Estimated Risk Score: {risk_score}/100

        Here are the individual stock summaries:
        {stock_summary_text}

        Based on the data given, generate a comprehensive summary of the portfolio.
        Include:
        - Overall performance and key metrics
        - Risk assessment and recommendations
        - Any notable trends or insights
        - Suggestions for future actions based on the risk tolerance and investment horizon
        - Also consider the individual stock advicecs provided. If there are any stocks with significant issues or recommendations, highlight them.
        - Also, provide a final recommendation on whether the user should rebalance, hold, or take any specific actions with their portfolio.
        - You should also relate the risk score to the risk tolerance and investment horizon provided.
        """,
        input_variables=["risk_tolerance", "horizon", "objective", "liquidity_needs","total_investment", "current_value",
                        "profit_loss", "profit_loss_percent", "diversification",
                        "risk_score", "stock_summary_text"]
    )

    chain = prompt | llm

    result = chain.invoke({
        "risk_tolerance":risk_tolerance,
        "horizon":horizon,
        "objective":objective,
        "liquidity_needs":liquidity_needs,
        "total_investment":round(total_investment, 2),
        "current_value":round(current_value, 2),
        "profit_loss":round(profit_loss, 2),
        "profit_loss_percent":profit_loss_percent,
        "diversification":diversification,
        "risk_score":risk_score,
        "stock_summary_text":stock_summary_text 
    })
    
    updated_summary= result.content
    print(f"Final summary generated: {updated_summary}")
    return {"summary": updated_summary}
    