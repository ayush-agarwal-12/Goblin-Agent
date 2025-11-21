from typing import Any,Dict
from ..workflows.state import AgentState
from ..tools.yfinance_tool import get_market_data,get_company_info
from ..tools.finnhub_tool import get_company_basic_financials,get_company_profile

async def collect_data(symbol: str, analysis_date : str) -> Dict[str, Any]:
    """
    Collect market data and news for a symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        analysis_date: Date for analysis in YYYY-MM-DD format (optional)
        
    Returns:
        Dict with collected data or error info
    """
    try:
        symbol = symbol.upper()
        
        # Collect market data
        market_result = await get_market_data(symbol, analysis_date)
        company_result = await get_company_info(symbol)
        profile_result = await get_company_profile(symbol)
        financials_result = await get_company_basic_financials(symbol)
        
        return {
            'symbol': symbol,
            'analysis_date': analysis_date,
            'market_data': market_result.data if market_result and market_result.success else None,
            'company_info': company_result.data if company_result and company_result.success else None,
            'company_profile': profile_result.data if profile_result and profile_result.success else None,
            'basic_financials': financials_result.data if financials_result and financials_result.success else None,
            'success': True
        }
        
    except Exception as e:
        print(f"Error collecting data for {symbol}: {e}")
        return {
            'symbol': symbol,
            'analysis_date': analysis_date,
            'success': False,
            'error': str(e)
        }
     
     
async def data_collection_agent_node(state:AgentState) -> AgentState:
    """
        LangGraph node for data collection.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with data collection results
    """

    try:
        # get symbol and analysis date from state
        symbol = state['symbol']
        analysis_date = state['analysis_date']

        # collect data
        result = await collect_data(symbol,analysis_date)

        # update state
        state['data_collection_results'] = result
        state['current_step'] = 'data_collection_complete'

        if not result['success']:
            state['error'] = result.get('error','Data collection failed')

        return state
    
    except Exception as e:
        print(f"Data collection node error: {e}")
        state['error'] = str(e)
        state['current_step'] = 'error'
        return state 