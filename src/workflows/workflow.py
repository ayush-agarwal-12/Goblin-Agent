from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from src.workflows.state import AgentState, create_initial_state
from src.Agents.data_collection_agent import data_collection_agent_node
from src.Agents.technical_analysis_agent import technical_analysis_agent_node
from src.Agents.news_intelligence_agent import news_intelligence_agent_node 
from src.Agents.portfolio_manager_agent import protfolio_manager_agent_node

def debug_state(state: AgentState, agent_name: str) -> AgentState:
    """Debug function to log state after each agent."""
    print(f"\n{agent_name} Agent Complete:")
    
    # Basic info
    analysis_date = state.get('analysis_date', 'N/A')
    symbol = state['symbol']

    # Data collection result
    data_result = state.get('data_collection_results')
    if data_result and agent_name == "data_collection":
        # market_data = data_result.get("market_data",{})
        success = data_result.get('success', False)
        print(f"Data Collection {success}")

    # Technical Analysis Results
    tech_results = state.get('technical_analysis_results')
    if tech_results and agent_name == "technical_analysis":
        success = tech_results.get('success', False)
        print(f"Technical Success: {success}")
    
    # News Intelligence Results
    news_results = state.get('news_intelligence_results')
    if news_results and agent_name == "news_intelligence":
        success = news_results.get('success', False)
        print(f"News Success: {success}")
    
    # Portfolio Manager Results
    portfolio_results = state.get('portfolio_manager_results')
    if portfolio_results and agent_name == "portfolio_manager":
        if portfolio_results.get('success', False):
            signal = portfolio_results.get('trading_signal', "Unknown")
            confidence_interval = portfolio_results.get('confidence_level', 0)
            volume = portfolio_results.get('position_size', 0)
            print(f"signal : {signal} , confidence interval : {confidence_interval} , volume : {volume}")
        print(f"Protfolio Analysis completed")
    
    # Error state
    if state.get('error'):
        print(f"Error: {state.get('error')}")

    print(f"\n")
    print(f"="*80)
    
    return state


async def debug_data_collection_node(state: AgentState) -> AgentState:
    """Data collection node with debug output"""
    result = await data_collection_agent_node(state)
    return debug_state(result, "data_collection")


async def debug_technical_analysis_node(state: AgentState) -> AgentState:
    """Technnical analysis node with debug output"""
    result = await technical_analysis_agent_node(state)
    return debug_state(result, "technical_analysis")


async def debug_news_intelligence_node(state: AgentState) -> AgentState:
    """News intelligence node with debug output"""
    result = await news_intelligence_agent_node(state)
    return debug_state(result, "news_intelligence")


async def debug_portfolio_manager_node(state: AgentState) -> AgentState:
    """Protfolio manager node with debug output"""
    result = await protfolio_manager_agent_node(state)
    return debug_state(result, "portfolio_manager")


def create_workflow() -> StateGraph:
    """
        create Langgraph workflow connecting all the agents

        Returns:
        Stategraph : configured workflow graph
    """
    # intialize workflows
    workflow = StateGraph(AgentState)

    # Add nodes with debug output
    workflow.add_node("data_collection", debug_data_collection_node)
    workflow.add_node("technical_analysis", debug_technical_analysis_node)
    workflow.add_node("news_intelligence", debug_news_intelligence_node)
    workflow.add_node("portfolio_manager", debug_portfolio_manager_node)
    
    # Define linear flow
    workflow.add_edge(START, "data_collection")
    workflow.add_edge("data_collection", "technical_analysis")
    workflow.add_edge("technical_analysis", "news_intelligence")
    workflow.add_edge("news_intelligence", "portfolio_manager")
    workflow.add_edge("portfolio_manager", END)
    
    return workflow.compile()


async def run_analysis(symbol: str, analysis_date: str, session_id: str = 'default') -> Dict[str, Any]:
    """
    Run complete analysis workflow for symbol.
        
        Args:
            symbols: stock symbol to analyze
            session_id: Session identifier
            analysis_date: Date for analysis in YYYY-MM-DD format (optional, defaults to today)
            
        Returns:
        Dict with analysis results
    """
    try:
        # create workflows
        workflow = create_workflow()

        # intialize state with analysis date 
        initial_state = create_initial_state(symbol, session_id, analysis_date)

        # Run workflow
        result = await workflow.ainvoke(initial_state)

        # extract result
        return {
            'success': True,
            'session_id': session_id,
            'analysis_date': analysis_date,
            'symbol': symbol,
            'results': {
                'data_collection': result.get('data_collection_results'),
                'technical_analysis': result.get('technical_analysis_results'),
                'news_intelligence': result.get('news_intelligence_results'),
                'portfolio_manager': result.get('portfolio_manager_results')
            },
            'final_step': result.get('current_step'),
            'error': result.get('error')
        }

    except Exception as e:
        print(f"workflow error {e}")
        return {
            'success': False,
            'error': str(e),
            'symbol': symbol,
            'session_id': session_id,
            'analysis_date': analysis_date
        }
