# GoblinAgent: Multi-Agent Financial Analysis System
## Overview

GoblinAgent is a multi-agent, LLM-powered stock analysis system built using LangGraph, FastAPI, and multiple data providers.

The agent orchestrates four specialized financial intelligence modules to produce:

Market & price analysis

Fundamental valuation metrics

Technical indicators

News sentiment intelligence

Final trading signal (Buy / Sell / Hold)

Confidence score

Recommended position size

GoblinAgent blends AI reasoning, quantitative indicators, and NLP sentiment extraction to deliver a unified investment-grade analysis in seconds.

# Core Architecture
## Multi-Agent Sequential Pipeline (LangGraph)

GoblinAgent uses a sequential workflow, where each specialized agent receives the current state, processes new information, and passes forward enhanced state data.

## Pipeline Structure

Data Collection Agent

Technical Analysis Agent

News Intelligence Agent

Portfolio Manager Agent (Final Decision Maker)

Each step adds unique insights, resulting in a rich, multi-dimensional stock evaluation.

# Agent Breakdown
## 1. Data Collection Agent

Aggregates raw market and company data:

Market Data

Current price

Previous closing price

Price change (absolute)

Price change (%)

Company Information

Company name

Sector & industry

Market capitalization

Country

Exchange

Business description

Fundamental Metrics

(From basic financials → metrics)

Valuation

P/E Ratio

P/B Ratio

Dividend Yield

Profitability

ROE

ROA

Net Profit Margin

EPS

Liquidity & Leverage

Current Ratio

Debt-to-Equity

Growth

Revenue Growth

This agent creates the full fundamental profile used downstream.

## 2. Technical Analysis Agent

Computes indicators using pricing history:

Trend Indicators

SMA (20-day)

EMA (20-day)

Momentum Indicators

RSI (14-period)

CCI (20-period)

Volatility Indicators

Bollinger Bands (Upper / Middle / Lower)

MACD Components

MACD line

Signal line

Histogram

Trend Strength

ADX

The agent interprets whether the stock is trending, consolidating, overbought, oversold, or volatile.

## 3. News Intelligence Agent

Extracts natural-language insights from real-time news feeds:

Per Article:

Headline

Source

Published date

Key bullet-point summaries

Sentiment (positive / negative / neutral)

Impact (low / medium / high)

Category (earnings, analyst rating, sector news, etc.)

Output:

Number of articles analyzed

Condensed news sentiment overview

Key insights influencing market behavior

This agent reveals psychological & macro-driven movement risks that fundamentals cannot capture.

## 4. Portfolio Manager Agent

This is the final decision-making module.

Inputs:

Market data

Fundamentals

Technical indicators

News sentiment

Outputs:

Trading Signal

BUY

SELL

HOLD

Confidence Level

Value from 0 → 1

Also represented as a percentage

Position Size

Recommended allocation (%) for the symbol

Adjusted for confidence and risk level

This produces the final investment-ready conclusion.

# How GoblinAgent Reaches Its Conclusion

GoblinAgent combines:

 Data Collection → Fair Value & Business Quality
 Technical Indicators → Momentum & Trend Direction
 News Sentiment → Short-Term Market Psychology
 Decision Agent → Risk-Adjusted Signal

Decision Logic (simplified):

Strong fundamentals + positive trend + positive news → BUY

Weak fundamentals + negative trend + negative news → SELL

Mixed or uncertain indicators → HOLD

The confidence score reflects alignment between these factors.
The position size scales with confidence.
