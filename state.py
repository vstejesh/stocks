from typing import TypedDict, Annotated
import pandas as pd
import operator
from langchain_core.messages import AnyMessage  # if you're using LangGraph

class StockInfo(TypedDict):
    ticker: str
    shares_held: float
    buy_price: float
    current_price: float
    sector: str
    purchase_date: str
    prices: pd.DataFrame
    news: pd.DataFrame
    price_analyst_report: str
    news_analyst_report: str
    recommendation: str  # "Buy", "Hold", "Sell", etc.

class PortfolioSummary(TypedDict):
    total_investment: float
    current_value: float
    profit_loss: float
    profit_loss_percent: float
    diversification: dict[str, float]  # {"IT": 50.0, "Energy": 30.0}
    risk_score: float
    overall_advice: str  # "Rebalance", "Stable", "Reduce exposure to X"

class AppState(TypedDict):
    user_uploaded_file: str  # file name or ID
    risk_tolerance: str      # "Low", "Medium", "High"
    investment_horizon: str  # "Short-term", "Medium-term", "Long-term"
    objective: str  # "Growth", "Income", "Balanced"
    liquidity_needs: str  # "High", "Medium", "Low"
    portfolio: list[StockInfo]
    summary: PortfolioSummary
    # final_response: Annotated[list[AnyMessage], operator.add]
    # messages: Annotated[list[AnyMessage], operator.add]
