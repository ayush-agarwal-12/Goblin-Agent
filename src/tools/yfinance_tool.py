import yfinance  as yf
from .utils import ToolResult

async def get_market_data(symbol : str,analysis_date : str , period : str = '3mo') -> ToolResult:
    """
        Get market data for a symbol for a specific date or latest data.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            analysis_date: Specific date for analysis in YYYY-MM-DD format (optional)
            period: Period for data (default: 3mo)
            
        Returns:
            ToolResult with market data
    """
    try:
        symbol = symbol.upper()
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)

        if data.empty:
            return ToolResult(
                success=False,
                error=f"No data available for {symbol}"
            )
        
        # Get latest data (for analysis_date)
        latest = data.iloc[-1]
        
        # Calculate price change if we have previous data
        previous_close = None
        price_change = None
        price_change_pct = None
        
        if len(data) >= 2:
            previous = data.iloc[-2]
            previous_close = float(previous['Close'])
            current_close = float(latest['Close'])
            price_change = current_close - previous_close
            price_change_pct = (price_change / previous_close) * 100 if previous_close != 0 else 0
        
        # Convert DataFrame to LangChain-compatible format (no Timestamp objects)
        historical_clean = data.reset_index()
        historical_clean['Date'] = historical_clean['Date'].dt.strftime('%Y-%m-%d')
        
        # Convert all numeric columns to regular Python types
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in historical_clean.columns:
                historical_clean[col] = historical_clean[col].astype(float)
        
        historical_dict = historical_clean.to_dict('records')
        
        result_data = {
            'symbol': symbol,
            'date': analysis_date,
            'current_price': float(latest['Close']),  # Add current price for easy access
            'price_data': {
                'open': float(latest['Open']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'close': float(latest['Close']),
                'volume': int(latest['Volume']),
                'previous_close': previous_close,
                'price_change': price_change,
                'price_change_pct': price_change_pct
            },
            'historical_data': historical_dict  # LangChain-friendly version only
        }

        price_data = result_data.get('price_data')
        print(f"current price : {result_data.get('current_price')}")
        print(f"previous closed : {price_data.get('previous_close')}")
        print(f"price change percentage : {price_data.get('price_change_pct')}%")
        print(f"\n")

        
        return ToolResult(success=True, data=result_data)

    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Error getting market data for {symbol} : {str(e)}"
        )
    

async def get_company_info(symbol : str) -> ToolResult:
    """
        Get company information for a symbol.
    
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            ToolResult with company info
    """
    try:
        symbol = symbol.upper()
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if not info:
            return ToolResult(
                success = False,
                error = f"No company info available for symbol : {symbol}"
            )

        company_data = {
            'symbol': symbol,
            'name': info.get('longName', info.get('shortName', 'N/A')),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'country': info.get('country', 'N/A'),
            'exchange': info.get('exchange', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'website': info.get('website', 'N/A'),
            'description': info.get('longBusinessSummary', 'N/A')[:500]  # Limit description
        }

        print(f"sector : {company_data.get('sector')}")
        print(f"industry : {company_data.get('industry')}")
        market_cap = company_data.get('market_cap',0)
        if market_cap >= 1_000_000_000_000:
            print( f"market cap : ${market_cap/1_000_000_000_000:.2f}T")
        elif market_cap >= 1_000_000_000:
            print(f"market cap : ${market_cap/1_000_000_000:.2f}B")
        else :
            print(f"market cap : ${market_cap/1_000_000:.2f}M") 
        print(f"country : {company_data.get('country')}")
        print(f"exchange : {company_data.get('exchange')}")
        print(f"description : {company_data.get('description')}")
        print(f"\n")
        
        return ToolResult(success=True, data=company_data)
    
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Error getting company info for {symbol}: {str(e)}"
        )