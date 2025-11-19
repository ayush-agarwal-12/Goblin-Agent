from ..workflows.state import AgentState
from typing import Optional,Dict,Any
import pandas as pd
from ..tools.technical_indicator_tool import calculate_technical_indicators

async def analyze_technical(symbol : str,analysis_date : str,market_data: Optional[Dict[str, Any]] = None)->Dict[str,Any]:
    """
    Calculate technical indicators for a symbol .
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        analysis_date: Date for analysis in YYYY-MM-DD format
        market_data: Optional market data from previous agent
        
    Returns:
        Dict with technical indicators or error info
    """
    try:
        if not market_data:
            return {
                'symbol':symbol,
                'success':False,
                'error' : f"No historical data available upto {analysis_date}"
            }
        
        if len(market_data['historical_data']) < 20:
            return {
                'symbol':symbol,
                'success':False,
                'error' : f"Insufficient historical data available upto {analysis_date}"
            }
        
        # Calculate technical indicators with dedicated tools
        indicators = ['SMA','EMA','RSI','MACD','BBANDS','ADX','CCI']

        # Ensure market_data is DataFrame
        hist_data_df = pd.DataFrame(market_data.get('historical_data'))
        result = await calculate_technical_indicators(hist_data_df,symbol,analysis_date,indicators)

        if not result.success:
            return{
                'symbol':symbol,
                'success' : False,
                'error' : result.error or "Technical analysis failed"
            }
        
        # Get current price from market data or last close price from filtered data
        current_price = 0.0
        if market_data and isinstance(market_data, dict) and 'current_price' in market_data:
            current_price = market_data['current_price']
        elif not hist_data_df.empty:
            current_price = float(hist_data_df['Close'].iloc[-1])
        
        # Add current price to indicators
        indicators_data = result.data if result.data else {}
        indicators_data['current_price'] = current_price
        
        return {
            'symbol': symbol,
            'indicators': indicators_data,
            'success': True
        }

        
    except Exception as e:
        print(f"error in technical analysis for {symbol}")
        return {
            'symbol':symbol,
            'success' : False,
            'error' : str(e)
        }



async def technical_analysis_agent_node(state : AgentState) -> AgentState:
    """
    LangGraph node for technical analysis.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with technical analysis results
    """
    try:
        # Get symbol,analysis date and market data from previous agent
        symbol = state['symbol']
        analysis_date = state['analysis_date']
        data_collection_results = state.get('data_collection_results')
        market_data = data_collection_results.get('market_data') if data_collection_results else None

        # perform technical analysis with analysis date
        result = await analyze_technical(symbol,analysis_date,market_data)

        # update state
        state['technical_analysis_results'] = result
        state['current_step'] = "technical_analysis_completed"

        if not result['success']:
            state['error'] = result.get('error','Technical analysis failed')

        return state
    
    except Exception as e:
        print(f"Technical Analysis node error : {e}")
        state['error'] = str(e)
        state['current_step'] = 'error'
        return state