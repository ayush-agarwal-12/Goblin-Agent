from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import warnings
import sys
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Project Setup
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

load_dotenv()

os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Goblin Agent"

from src.workflows.workflow import run_analysis


# FASTAPI App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request / Response Model
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


# Helper Functions
def safe_get(dictionary, *keys, default="N/A"):
    """Safely extract nested dictionary values."""
    if dictionary is None:
        return default
    result = dictionary
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    return result if result is not None else default


def format_currency(value):
    try:
        return f"${float(value):,.2f}"
    except:
        return "N/A"


def format_percentage(value):
    try:
        return f"{float(value):.2f}%"
    except:
        return "N/A"


def format_billions(value):
    try:
        return f"${float(value)/1_000_000_000:.2f}B"
    except:
        return "N/A"



# MAIN AGENT FUNCTION
async def run_agent(message: str) -> str:
    """Run the Goblin workflow and return a formatted summary."""

    warnings.filterwarnings("ignore", message=".*UUID v7.*")

    symbol = message.strip().upper()
    analysis_date = datetime.today().date().strftime("%Y-%m-%d")
    session_id = f"analysis_{datetime.now()}"

    try:
        result = await run_analysis(symbol, analysis_date, session_id)

        if not result.get("success"):
            return f"Analysis failed: {result.get('error', 'Unknown error')}"

        results = result.get("results", {})

        # DATA COLLECTION
        data = results.get("data_collection", {})
        market_data = safe_get(data, "market_data", default={})
        price_data = safe_get(market_data, "price_data", default={})
        company_info = safe_get(data, "company_info", default={})
        basic_financials = safe_get(data, "basic_financials", default={})
        metrics = safe_get(basic_financials, "metrics", default={})

        # TECHNICALS
        technical = results.get("technical_analysis", {})
        indicators = safe_get(technical, "indicators", default={})
        tech_data = safe_get(indicators, "technical_indicators", default={})

        # NEWS
        news = results.get("news_intelligence", {})
        nlp_features = safe_get(news, "nlp_features", default={})
        news_features = safe_get(nlp_features, "news_features", default=[])

        # PORTFOLIO
        portfolio = results.get("portfolio_manager", {})
        portfolio_data = safe_get(portfolio, symbol, default={})


        # BUILD SUMMARY (PLAIN TEXT - NO HTML)
        lines = []
        lines.append("=" * 70)
        lines.append("GOBLIN - FINANCIAL ANALYST")
        lines.append(f"Symbol: {symbol} | Date: {analysis_date}")
        lines.append("=" * 70)
        lines.append("")
        
        lines.append("MARKET DATA")
        lines.append("-" * 70)
        lines.append(f"Current Price:      {format_currency(safe_get(market_data, 'current_price'))}")
        lines.append(f"Previous Close:     {format_currency(safe_get(price_data, 'previous_close'))}")
        lines.append(f"Price Change:       {format_currency(safe_get(price_data, 'price_change'))} ({format_percentage(safe_get(price_data, 'price_change_pct'))})")
        lines.append("")
        lines.append(f"Company:            {safe_get(company_info, 'name')}")
        lines.append(f"Sector:             {safe_get(company_info, 'sector')}")
        lines.append(f"Industry:           {safe_get(company_info, 'industry')}")
        lines.append(f"Market Cap:         {format_billions(safe_get(company_info, 'market_cap'))}")
        lines.append("")
        
        desc = safe_get(company_info, 'description', default='N/A')
        lines.append(f"Description: {desc}...")
        lines.append("")

        lines.append("FUNDAMENTAL METRICS")
        lines.append("-" * 70)
        lines.append(f"P/E Ratio:          {safe_get(metrics, 'peBasicExclExtraTTM')}")
        lines.append(f"P/B Ratio:          {safe_get(metrics, 'pbAnnual')}")
        lines.append(f"Dividend Yield:     {format_percentage(safe_get(metrics, 'dividendYieldIndicatedAnnual', 0))}")
        lines.append("")
        lines.append(f"ROE:                {format_percentage(safe_get(metrics, 'roeRfy'))}")
        lines.append(f"ROA:                {format_percentage(safe_get(metrics, 'roaRfy'))}")
        lines.append(f"Profit Margin:      {format_percentage(safe_get(metrics, 'netProfitMarginTTM'))}")
        lines.append(f"EPS:                {format_currency(safe_get(metrics, 'epsBasicExclExtraItemsTTM'))}")
        lines.append("")
        lines.append(f"Current Ratio:      {safe_get(metrics, 'currentRatioAnnual')}")
        lines.append(f"Debt/Equity:        {safe_get(metrics, 'totalDebt/totalEquityAnnual')}")
        lines.append(f"Revenue Growth:     {format_percentage(safe_get(metrics, 'revenueGrowthTTM'))}")
        lines.append("")

        lines.append("TECHNICAL INDICATORS")
        lines.append("-" * 70)
        lines.append(f"SMA (20):           {safe_get(tech_data, 'SMA')}")
        lines.append(f"EMA (20):           {safe_get(tech_data, 'EMA')}")
        lines.append(f"RSI (14):           {safe_get(tech_data, 'RSI')}")
        lines.append(f"ADX (14):           {safe_get(tech_data, 'ADX')}")
        lines.append(f"CCI (20):           {safe_get(tech_data, 'CCI')}")
        lines.append("")
        lines.append(f"MACD Line:          {safe_get(tech_data, 'MACD', 'macd')}")
        lines.append(f"MACD Signal:        {safe_get(tech_data, 'MACD', 'signal')}")
        lines.append(f"MACD Histogram:     {safe_get(tech_data, 'MACD', 'histogram')}")
        lines.append("")
        lines.append(f"BB Upper:           {safe_get(tech_data, 'BBANDS', 'upper')}")
        lines.append(f"BB Middle:          {safe_get(tech_data, 'BBANDS', 'middle')}")
        lines.append(f"BB Lower:           {safe_get(tech_data, 'BBANDS', 'lower')}")
        lines.append("")

        lines.append("NEWS ANALYSIS")
        lines.append("-" * 70)
        lines.append(f"Articles Analyzed:  {len(news_features)}")
        lines.append("")

        for i, article in enumerate(news_features[:3], 1):
            headline = safe_get(article, "headline", default="No headline")
            sentiment = safe_get(article, "sentiment", default="neutral").upper()
            
            lines.append(f"Article {i}:  {sentiment}")
            lines.append(f"  {headline}...")
            lines.append("")

        lines.append("PORTFOLIO RECOMMENDATION")
        lines.append("-" * 70)

        if portfolio_data and safe_get(portfolio_data, "success"):
            signal = safe_get(portfolio_data, 'trading_signal', default='HOLD')
            confidence = safe_get(portfolio_data, 'confidence_level', default=0)
            position = safe_get(portfolio_data, 'position_size', default=0)
            
            
            lines.append(f"Signal:             {signal}")
            lines.append(f"Confidence:         {confidence:.1f}/1.0 ({confidence*100:.0f}%)")
            lines.append(f"Position Size:      {position}%")
        else:
            lines.append("Portfolio analysis unavailable")

        lines.append("")
        lines.append("=" * 70)
        lines.append("End of Analysis")
        lines.append("=" * 70)

        return "\n".join(lines)

    except Exception as e:
        import traceback
        error_lines = [
            "=" * 70,
            "ERROR",
            "=" * 70,
            str(e),
            "",
            "Stack Trace:",
            traceback.format_exc(),
            "=" * 70
        ]
        return "\n".join(error_lines)



# Endpoint
@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    reply = await run_agent(request.message)
    return ChatResponse(reply=reply)



# Static UI
app.mount("/", StaticFiles(directory="static", html=True), name="static")