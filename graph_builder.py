from langgraph.graph import StateGraph
# from typing import TypedDict, Annotated
# import operator
from langchain_core.messages import AnyMessage
from state import AppState

from nodes import (
    load_portfolio,
    price_history_node,
    news_fetch_node,
    price_analysis_node,
    news_analysis_node,
    stock_advice_node,
    summarize_node,
    # final_response_node
)

# 1. Initialize the graph
builder = StateGraph(AppState)

# 2. Add each node (these names are string references to actual functions)
builder.add_node("load_portfolio", load_portfolio)
builder.add_node("price_history", price_history_node)
builder.add_node("news_fetcher", news_fetch_node)
builder.add_node("price_analyzer", price_analysis_node)
builder.add_node("news_analyzer", news_analysis_node)
builder.add_node("stock_adviser", stock_advice_node)
builder.add_node("portfolio_summary", summarize_node)
# builder.add_node("final_response", final_response_node)


# 3. Define the edges (transitions between nodes)
builder.set_entry_point("load_portfolio")

builder.add_edge("load_portfolio", "price_history")
builder.add_edge("price_history", "news_fetcher")
builder.add_edge("news_fetcher", "price_analyzer")
builder.add_edge("price_analyzer", "news_analyzer")
builder.add_edge("news_analyzer", "stock_adviser")
builder.add_edge("stock_adviser", "portfolio_summary")
# builder.add_edge("portfolio_summary", "final_response")

builder.set_finish_point("portfolio_summary")

# 4. Build the graph
graph = builder.compile()