import finnhub
import asyncio
from datetime import datetime,timedelta
from .utils import ToolResult
from dotenv import load_dotenv
import os

load_dotenv()
finnhub_api_key = os.getenv('FINNHUB_API_KEY')


async def _apply_rate_limiting():
    """Apply rate limiting for Finnhub API calls."""
    # Use existing news rate limiting config (60 seconds / max_per_minute)
    rate_limit = 60.0 / 50 
    if rate_limit > 0:
        await asyncio.sleep(rate_limit)

def _get_finnhub_client():
    """"Get finnhub client with api key from config"""
    finnhub_key = finnhub_api_key
    if not finnhub_key:
        return None
    
    return finnhub.Client(api_key=finnhub_key)

async def get_company_basic_financials(symbol : str,metric : str = "all") -> ToolResult:
    """Get company basic financial metric"""
    client = _get_finnhub_client()
    if not client:
        return ToolResult(
            success=False,
            error=f"Finnhub api_key not configured"
        )
    
    symbol = symbol.upper()
    
    try:
        await _apply_rate_limiting()
        result = client.company_basic_financials(symbol,metric)

        if not result or 'metric' not in result:
            return ToolResult(success=False, error=f"No financial data found for {symbol}")
        
        imp_ratios = result.get('metric')
        print(f"PE Ratio : {imp_ratios.get('peBasicExclExtraTTM')}")
        print(f"PB Ratio : {imp_ratios.get('pbAnnual')}")
        print(f"ROE : {imp_ratios.get('roeRfy')}")
        print(f"ROA : {imp_ratios.get('roaRfy')}")
        print(f"Debt To Equity : {imp_ratios.get('totalDebt/totalEquityAnnual')}")
        print(f"Current Ration : {imp_ratios.get('currentRatioAnnual')}")
        print(f"Profit Margin : {imp_ratios.get('netProfitMarginTTM')}")
        print(f"Revenue Growth : {imp_ratios.get('revenueGrowthTTM')}")
        print(f"EPS : {imp_ratios.get('epsBasicExclExtraItemsTTM')}")
        print(f"Dividend Yield : {imp_ratios.get('dividendYieldIndicatedAnnual')}")

        return ToolResult(
            success=True,
            data={
                'symbol':symbol,
                'metrics' : result['metric'],
                'series': result.get('series', {}),
                'updated': datetime.now().isoformat()
            }
        )

    except Exception as e:
        return ToolResult(success=False,error=f"Failed to fetch financial analysis for {symbol}")
    
async def get_company_profile(symbol : str) -> ToolResult:
    """Get company profile information"""
    client = _get_finnhub_client()
    if not client:
        return ToolResult(
            success=False,
            error=f"Finnhub api_key not configured"
        )
    
    symbol = symbol.upper()

    try:
        await _apply_rate_limiting()
        result = client.company_profile2(symbol=symbol)

        if not result:
            return ToolResult(success=False,error=f"No company profile found for {symbol}")
        
        return ToolResult(
            success=True,
            data={
                'symbol': result.get('ticker', symbol),
                'name': result.get('name', ''),
                'country': result.get('country', ''),
                'currency': result.get('currency', ''),
                'exchange': result.get('exchange', ''),
                'industry': result.get('finnhubIndustry', ''),
                'ipo': result.get('ipo', ''),
                'logo': result.get('logo', ''),
                'market_cap': result.get('marketCapitalization', 0),
                'employees': result.get('shareOutstanding', 0),
                'weburl': result.get('weburl', '')
            }
        )

    except Exception as e:
        return ToolResult(success=False,error=f"Failed to fetch comapny profile : {str(e)}")
    
async def get_company_news(symbol:str,analysis_date:str)->ToolResult:
    """
        Get latest  company news

        Args:
            Symbol : Stock Symbol
            Analysis Date : Current Date

        Return ToolResult with latest comapny news
    """

    client = _get_finnhub_client()
    if not client:
        return ToolResult(success=False,error="finnhub API key not configured")
    
    try:
        await _apply_rate_limiting()

        end_date = datetime.strptime(analysis_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=5)

        # Convert datetime objects to strings in YYYY-MM-DD format
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")

        # make API call
        result = client.company_news(symbol=symbol,_from = start_date,to=end_date)
        news_items = result if isinstance(result, list) else []

        return ToolResult(
            success=True,
            data={
                'symbol': symbol,
                'news': news_items,
                'total_count': len(news_items),
                'period': f"{start_date} to {end_date}",
                'trading_session': analysis_date is not None
            }
        )


    except Exception as e:
        return ToolResult(success=False,error=f"Failed to fetch {symbol} news : {str(e)}")