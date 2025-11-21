Goblin Agent – Stock Analysis & Trading Signal Agent

Goblin Agent is an LLM-powered financial analysis workflow that takes a stock symbol (e.g. AAPL) and returns a structured, human-readable report including:

Market data

Fundamental ratios

Technical indicators

News & sentiment analysis

A final trading conclusion (signal, confidence, position size)

It is wired into a FastAPI backend with a simple chat-style UI, so you can type a symbol and get a full analysis in one place.

1. How Goblin Agent Works

The core entrypoint of the workflow is:

from src.workflows.workflow import run_analysis


When you pass a stock symbol to run_analysis(symbol, analysis_date, session_id), the agent executes several stages:

Data Collection Agent

Fetches market data (current price, previous close, price change, price change %).

Fetches company info (name, sector, industry, market cap, country, exchange, description).

Fetches basic financials / metrics for fundamentals and ratios.

Technical Analysis Agent

Computes indicators like SMA, EMA, RSI, MACD, Bollinger Bands, ADX, CCI from historical price data.

News Intelligence Agent

Downloads recent news for the ticker.

Extracts headline, source, key points, sentiment, impact, category per article.

Builds higher-level NLP features that summarize overall sentiment.

Portfolio Manager Agent (Final Conclusion)

Looks at:

Market data

Fundamental ratios

Technical indicators

News sentiment

Produces a final decision:

trading_signal – e.g. BUY, SELL, or HOLD

confidence_level – value between 0 and 1

position_size – recommended allocation in %

The FastAPI endpoint calls run_analysis(...), then formats all of this into a single multi-section text summary for the UI.

2. What the Report Includes
2.1 Market Data

Keys (from market_data and price_data):

current_price

previous_close

price_change

price_change_pct

The report shows, for example:

Current Price – latest trading price

Previous Close – last close price

Price Change – absolute change

Price Change % – percentage move since previous close

2.2 Company Information

Keys (from company_info):

name

sector

industry

market_cap

country

exchange

description

This describes what the company does, in which sector/industry it operates, where it is listed, and its approximate size (market cap).

2.3 Fundamental Metrics (Financial Ratios)

Keys (from metrics inside basic_financials):

Valuation

peBasicExclExtraTTM – P/E ratio (price vs earnings)

pbAnnual – P/B ratio (price vs book value)

dividendYieldIndicatedAnnual – dividend yield

Profitability

roeRfy – Return on Equity

roaRfy – Return on Assets

netProfitMarginTTM – net profit margin

epsBasicExclExtraItemsTTM – earnings per share

Liquidity & Leverage

currentRatioAnnual – current ratio (short-term liquidity)

totalDebt/totalEquityAnnual – debt-to-equity ratio

Growth

revenueGrowthTTM – revenue growth over trailing twelve months

These ratios explain how expensive the stock is, how profitable it is, how leveraged it is, and whether it is growing.

2.4 Technical Indicators

Keys (from technical_indicators / tech_data):

SMA – Simple Moving Average (trend)

EMA – Exponential Moving Average (trend, recent prices weighted more)

RSI – Relative Strength Index (overbought/oversold momentum)

MACD – Moving Average Convergence Divergence (trend & momentum)

macd

signal

histogram

BBANDS – Bollinger Bands (volatility)

upper

middle

lower

ADX – Average Directional Index (trend strength)

CCI – Commodity Channel Index (momentum / deviation from typical price)

These help determine whether the stock is trending, range-bound, or overbought/oversold.

2.5 News & Sentiment Analysis

From news_intelligence_results → nlp_features → news_features:

Per article:

headline

published_date

source

key_points (bullet-style summary)

sentiment (e.g. positive / negative / neutral)

impact (e.g. low / medium / high)

category (e.g. earnings, analyst rating, etc.)

The report:

Counts total articles analyzed.

Shows a few top articles (headline + key points).

Uses sentiment to understand whether news is supportive, negative, or mixed for the stock.

2.6 Final Conclusion

From portfolio_manager_results (often under portfolio_result[symbol]):

trading_signal – final decision:

BUY – expected upside / favorable conditions

SELL – downside risk / overvaluation / negative setup

HOLD – uncertain or fairly valued

confidence_level:

Float between 0 and 1

Also expressed as a percentage in the text summary

position_size:

Recommended allocation in % of your portfolio (e.g. 20%, 60%, etc.)

How it gets to the conclusion (logic):

High level, the portfolio manager agent:

Reads:

Trend & momentum from technical indicators

Valuation & profitability from fundamentals

Overall bias from news sentiment

Weighs the evidence:

Strong fundamentals + positive trend + positive news → more likely BUY with higher confidence & larger position size.

Weak fundamentals + negative trend + bad news → more likely SELL.

Mixed / conflicting signals → HOLD or small position.

Converts this reasoning into the final trading_signal, confidence_level, and position_size.
