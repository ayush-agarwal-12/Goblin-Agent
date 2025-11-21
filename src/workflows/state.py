from typing import TypedDict, Dict, Any, Optional
from datetime import datetime

# Import NotRequired (needed to make fields disappear from UI input)
try:
    from typing import NotRequired
except ImportError:
    from typing_extensions import NotRequired

class AgentState(TypedDict):
    """
    Unified state structure for all Goblin agents.
    """
    # --- INPUT: ONLY Symbol is strictly required by the user ---
    symbol: NotRequired[str]

    # --- OPTIONAL INPUTS (UI won't ask for them, logic fills them) ---
    session_id: NotRequired[str]
    analysis_date: NotRequired[str] 
    current_step: NotRequired[str]

    # --- OUTPUTS (Calculated later, so not required at start) ---
    data_collection_results: NotRequired[Dict[str, Any]]
    news_intelligence_results: NotRequired[Dict[str, Any]]
    technical_analysis_results: NotRequired[Dict[str, Any]]
    portfolio_manager_results: NotRequired[Dict[str, Any]]

    # --- ERROR HANDLING ---
    error: NotRequired[str]

# Keep your helper function (used by main.py)
def create_initial_state(symbol: str, session_id: str, analysis_date: str) -> AgentState:
    if analysis_date is None:
        analysis_date = datetime.now().strftime("%Y-%m-%d")
        
    return {
        "symbol": symbol,
        "session_id": session_id,
        "analysis_date": analysis_date,
        "current_step": "initialized",
        # We don't need to set the others to None explicitly anymore
        # because they are NotRequired
    }