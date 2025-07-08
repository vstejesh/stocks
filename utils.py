from typing import cast
from state import StockInfo, AppState
import time
import pandas as pd
from datetime import timedelta, datetime 
import finnhub
import os
from dotenv import load_dotenv
from langchain_core import HumanMessage
from langchain_core.prompts import PromptTemplate

from langchain_groq import ChatGroq

llm = ChatGroq(
    temperature=0,
    model_name="llama-3.1-8b-instant",
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Initialize the Finnhub client
load_dotenv()
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY")) 


def date_to_unix(date_str: str) -> int:
    return int(time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple()))


from openbb import obb
import pandas as pd
from datetime import datetime

# Login (only needs to be done once per session)
# obb.login("OPENBB_API_KEY")

def get_price_history(ticker: str, start: str, end: str) -> pd.DataFrame:
    try:
        obb_obj = obb.equity.price.historical(
            symbol=ticker,
            start_date=start,
            end_date=end,
            interval="1d"
        )
        df = obb_obj.to_df()

        if df.empty:
            raise ValueError("No data returned")

        # If 'date' is missing, reset index and try again
        if 'date' not in df.columns:
            df = df.reset_index()

        # Check again after reset
        if 'date' not in df.columns:
            raise ValueError("Missing 'date' column even after reset")

        df = df.rename(columns={
            "date": "date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume"
        })

        df["date"] = pd.to_datetime(df["date"]).dt.strftime('%Y-%m-%d')

        return df[["date", "open", "high", "low", "close", "volume"]]

    except Exception as e:
        raise ValueError(f"Error fetching price history for {ticker} - {e}")



def get_news(ticker: str) -> pd.DataFrame:
    '''
    # Fetch recent news for a given stock ticker using the Finnhub API.

    # Args:
    #     ticker (str): Stock ticker symbol.
    #     days (int): Number of past days to look back for news.

    # Returns:
    #     pd.DataFrame: News articles with datetime, headline, source, and URL.
    '''
    days=10
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    # Format dates as YYYY-MM-DD
    from_str = from_date.strftime('%Y-%m-%d')
    to_str = to_date.strftime('%Y-%m-%d')

    # Get news from API
    news_list = finnhub_client.company_news(ticker, _from=from_str, to=to_str)

    if not news_list:
        return pd.DataFrame()

    # Convert list of dicts to DataFrame
    df = pd.DataFrame(news_list)

    # Select and rename relevant columns
    df = df[["datetime", "headline", "source", "url"]]
    df["datetime"] = pd.to_datetime(df["datetime"], unit='s')
    df = df.sort_values("datetime", ascending=False)

    return df

def get_price_analysis(ticker: str, prices: pd.DataFrame) -> str:
    '''
    # Simulate a price analysis report for a given stock ticker.

    # Args:
    #     ticker (str): Stock ticker symbol.
    #     prices (pd.DataFrame): DataFrame containing historical prices.

    # Returns:
    #     str: Simulated price analysis report.
    '''
    if prices.empty:
        return "No price data available"

    csv_data = prices.reset_index().to_csv(index=False)

    # Simulate a price analysis report
    prompt=PromptTemplate(
        template="""
        You are a highly skilled and detail-oriented financial analyst and equity researcher. You have been given a csv file named {prices} that contains 4 months of historical daily stock price data for the company {ticker}. The DataFrame contains the following columns:

        - `date`: trading date (string, format YYYY-MM-DD)
        - `open`: opening price of the stock
        - `high`: intraday high price
        - `low`: intraday low price
        - `close`: closing price
        - `volume`: number of shares traded

        Your task is to analyze the stock’s **performance over the last 4 months** and extract meaningful short-term and long-term trends. Perform the analysis as follows:

        ---

        ### 1. **Overview of Price Behavior**
        - Describe the overall trend (upward, downward, sideways) across the full 4 months.
        - Mention any periods of high volatility or price compression.
        - Identify the highest and lowest closing prices and when they occurred.

        ---

        ### 2. **Short-Term Trends (last 2–4 weeks)**
        - Is the stock showing recent momentum? If yes, is it bullish or bearish?
        - Note any recent support or resistance levels forming.
        - Mention any breakouts or breakdowns in price levels.
        - Has the stock shown higher highs/lows or lower highs/lows recently?

        ---

        ### 3. **Medium-to-Long-Term Trend Analysis**
        - Analyze the trend over the entire 4-month window:
        - Use structure: higher highs and higher lows vs lower highs and lower lows.
        - Observe whether the stock is forming a base, breakout, pullback, or reversal.
        - Evaluate consistency of the trend and whether volume supports the trend.

        ---

        ### 4. **Moving Averages and Crossovers**
        - Simulate 10-day, 20-day, and 50-day simple moving averages.
        - If possible, detect golden cross or death cross behavior.
        - Indicate whether the current price is above or below these key averages.

        ---

        ### 5. **Volume Analysis**
        - Identify surges in volume and whether they coincide with price movement (confirmations or divergence).
        - Is volume increasing or decreasing as price trends evolve?

        ---

        ### 6. **Volatility Patterns**
        - Identify periods of contraction or expansion in trading range.
        - Discuss ATR (Average True Range) or general volatility behavior even qualitatively.

        ---

        ### 7. **Conclusion**
        - Provide a summary of the current market structure (bullish, bearish, indecisive).
        - Give a realistic outlook over the next 2–4 weeks (short-term) and 1–2 months (longer-term), based on the data alone — no external factors.
        - If appropriate, suggest whether a cautious, neutral, or aggressive stance is justified for a trader.

        ---

        Avoid financial advice. Focus purely on data analysis and chart-based behavior. Be precise with your answers, using the data provided in the CSV file.
        Output your findings in a structured point wise format so it could be used as a prompt for further analysis or decision-making.
        """,
        input_variables=["prices"]
    )
    chain = prompt | llm
    result = chain.invoke({"prices": csv_data})

    return result.content

def get_news_analysis(ticker: str, news: pd.DataFrame) -> str:
    '''
    # Simulate a news analysis report for a given stock ticker.

    # Args:
    #     ticker (str): Stock ticker symbol.
    #     news (pd.DataFrame): DataFrame containing recent news articles.

    # Returns:
    #     str: Simulated news analysis report.
    '''
    if news.empty:
        return "No news data available"

    csv_data = news.reset_index().to_csv(index=False)

    prompt=PromptTemplate(
        template="""
        You are a financial analyst specializing in market sentiment analysis. You have been given a csv file named {news} that contains recent news articles related to the company {ticker}. The DataFrame contains the following columns:

        - `datetime`: date and time of the article
        - `headline`: title of the article
        - `source`: source of the article
        - `url`: link to the full article

        Your task is to analyze the sentiment and impact of these news articles on the stock's performance. Perform the analysis as follows:

        ---

        ### 1. **Sentiment Analysis**
        - Determine whether the overall sentiment is positive, negative, or neutral.
        - Identify any particularly impactful headlines and their sentiment.

        ---

        ### 2. **Source Credibility**
        - Evaluate the credibility of sources (e.g., major financial outlets vs social media).
        - Are there any sources that consistently provide positive or negative coverage?

        ---

        ### 3. **Trends Over Time**
        - Identify any trends in sentiment over the past few weeks.
        - Are there periods of heightened positive or negative sentiment?

        ---

        ### 4. **Correlation with Price Movement**
        - Discuss how recent price movements correlate with news sentiment.
        - Are there instances where negative news did not lead to expected price drops?

        ---

        ### 5. **Conclusion**
        - Provide an overall assessment of how current news sentiment may impact future stock performance.
        - If appropriate, suggest whether investors should be cautious, optimistic, or neutral based on recent coverage.

        ---

        Avoid financial advice. Focus purely on data analysis and sentiment extraction from the provided articles.
        Output your findings in a structured point wise format so it could be used as a prompt for further analysis or decision-making.
        """,
        input_variables=["news"]
    )
    chain = prompt | llm
    result = chain.invoke({"news": csv_data})
    return result.content

def get_stock_advice(ticker:str, price_analysis: str, news_analysis: str, risk_tolerance: str, investment_horizon: str) -> str:
    '''
    # Generate stock advice based on price and news analysis.

    # Args:
    #     ticker (str): Stock ticker symbol.
    #     price_analysis (str): Price analysis report.
    #     news_analysis (str): News analysis report.
    #     risk_tolerance (str): User's risk tolerance level.
    #     investment_horizon (str): User's investment horizon.

    # Returns:
    #     str: Stock advice.
    '''
    
    prompt=PromptTemplate(
        template="""
        You are a financial advisor specializing in stock recommendations. Based on the following analyses for {ticker}:

        ---

        ### Price Analysis
        {price_analysis}

        ---

        ### News Analysis
        {news_analysis}

        ---

        ### Risk Tolerance
        {risk_tolerance}

        ### Investment Horizon
        {investment_horizon}

        Your task is to provide a concise recommendation for investors. Consider the following:

        - Current market conditions and trends
        - Risk factors associated with the stock
        - Potential returns based on analysis

        Provide your recommendation in a single sentence, clearly stating whether to "Buy", "Hold", or "Sell" the stock, which is then followed by a justification of your recommendation. 
        The justification should be based on the provided analyses and should not include any external factors or personal opinions. 
        You should clearly mention the analysis that led to your recommendation. 
        In short you should briefly explain both price and news analyses and how they relate to the recommendation.
        """,
        input_variables=["ticker", "price_analysis", "news_analysis", "risk_tolerance", "investment_horizon"]
    )
    
    chain = prompt | llm
    result = chain.invoke({
        "ticker": ticker,
        "price_analysis": price_analysis,
        "news_analysis": news_analysis,
        "risk_tolerance": risk_tolerance,
        "investment_horizon": investment_horizon
    })
    
    return result.content
