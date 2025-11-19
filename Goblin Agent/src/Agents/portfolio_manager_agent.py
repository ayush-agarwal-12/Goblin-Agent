from ..workflows.state import AgentState
from typing import Optional,Dict,Any
import os,json
from langchain_groq import ChatGroq
from ..prompts.prompts import get_portfolio_manager_template


async def generate_trading_signal_with_prompts(
        symbol: str,
        tech_results: Optional[Dict[str, Any]],
        data_collection_results: Optional[Dict[str, Any]],
        news_data: Optional[Dict[str, Any]],
        analysis_date: str
) -> Optional[Dict[str, Any]]:
    """
    Generate trading signal using proper Portfolio Manager prompts.
    """
    try:
        # Get Groq API key
        api_key = os.getenv('GROQ_API_KEY')

        if not api_key:
            print(f"No Groq API Key found")
            return None
        
        # LLM without structured output
        llm = ChatGroq(
            model='openai/gpt-oss-120b',
            api_key=api_key,
            temperature=0.7,
            max_tokens=1000
        )

        # Get current price from technical data
        indicators_data = tech_results.get('indicators', {})
        technical_indicators = indicators_data.get('technical_indicators', {})
        current_price = indicators_data.get('current_price', 0)
        sma = technical_indicators.get('SMA')
        ema = technical_indicators.get('EMA')
        rsi = technical_indicators.get('RSI')
        macd = technical_indicators.get('MACD')
        bbands = technical_indicators.get('BBANDS')
        adx = technical_indicators.get('ADX')
        cci = technical_indicators.get('CCI')
    
        
        if current_price is None or current_price <= 0:
            print(f"No valid current price available for {symbol}")
            return None
        
        # Reduce financials to only ESSENTIAL metrics
        basic_financials_raw = data_collection_results.get('basic_financials', {})
        metrics = basic_financials_raw.get('metrics', {}) if basic_financials_raw else {}
        
        essential_financials = {
            'pe_ratio': metrics.get('peBasicExclExtraTTM'),
            'pb_ratio': metrics.get('pbAnnual'),
            'roe': metrics.get('roeRfy'),
            'roa': metrics.get('roaRfy'),
            'debt_equity': metrics.get('totalDebt/totalEquityAnnual'),
            'current_ratio': metrics.get('currentRatioAnnual'),
            'profit_margin': metrics.get('netProfitMarginTTM'),
            'revenue_growth': metrics.get('revenueGrowthTTM'),
            'eps': metrics.get('epsBasicExclExtraItemsTTM'),
            'dividend_yield': metrics.get('dividendYieldIndicatedAnnual')
        }
        
        company_profile = data_collection_results.get('company_profile', {})
        profile_data = {
            'name': company_profile.get('name', symbol),
            'industry': company_profile.get('industry', 'Unknown'),
            'market_cap': company_profile.get('market_cap', 0)
        }

        market_data = data_collection_results.get('market_data', {})
        price_data = market_data.get('price_data', {})
        
        historical_summary = {
            'prev_close': price_data.get('previous_close'),
            'change': price_data.get('price_change'),
            'change_pct': price_data.get('price_change_pct')
        }
        
        news_features = news_data.get('nlp_features', {}).get('news_features', [])
        minimal_news = []
        for article in news_features[:2]:
            minimal_news.append({
                'headline': article.get('headline', '')[:80],
                'sentiment': article.get('sentiment', 'neutral'),
                'top_point': article.get('key_points', [''])[0][:100] if article.get('key_points') else ''
            })


        prompt_input = {
            "symbol": symbol,
            "current_price": current_price,
            "sma" : sma,
            "ema" : ema,
            "macd" : macd,
            "rsi" : rsi,
            "bbands" : bbands,
            "adx" : adx,
            "cci" : cci,
            "moving_average" : sma[0]/ema[0],
            "financials": essential_financials,
            "company_profile": profile_data,
            "news": minimal_news,
            "history": historical_summary,
            "analysis_date": analysis_date
        }

        # Get prompt template
        prompt_template = get_portfolio_manager_template()

        # Create and execute chain (NO structured output)
        chain = prompt_template | llm 
        result = await chain.ainvoke(prompt_input)
        
        # Parse the result
        if hasattr(result, 'content'):
            result_content = result.content.strip()
            
            try:
                # Extract JSON from response
                if "```json" in result_content:
                    start = result_content.find("```json") + 7
                    end = result_content.find("```", start)
                    json_str = result_content[start:end].strip() if end > start else result_content[start:].strip()
                    result = json.loads(json_str)
                elif "```" in result_content:
                    start = result_content.find("```") + 3
                    end = result_content.find("```", start)
                    json_str = result_content[start:end].strip() if end > start else result_content[start:].strip()
                    result = json.loads(json_str)
                else:
                    result = json.loads(result_content)
                
                # Normalize keys to handle any format
                if isinstance(result, dict):
                    normalized = {}
                    for key, value in result.items():
                        normalized_key = key.lower().replace(' ', '_').replace('-', '_')
                        normalized[normalized_key] = value
                    result = normalized
                    print(f"Final Conclusion : {result}")
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse LLM response: {e}")
                return None
        
        # Validate result
        if isinstance(result, dict):
            required_fields = ['trading_signal', 'confidence_level', 'position_size']
            
            for field in required_fields:
                if field not in result:
                    print(f"Missing {field} in portfolio result")
                    print(f"Available keys: {list(result.keys())}")
                    return None
            
            signal = str(result.get('trading_signal', '')).upper()
            if signal not in ['BUY', 'SELL', 'HOLD']:
                print(f"Invalid trading signal: {signal}")
                return None
            
            try:
                confidence = float(result.get('confidence_level', 0))
                position = int(result.get('position_size', 0))
                
                # Validate and clamp values
                confidence = max(0.1, min(1.0, round(confidence, 1)))
                position = max(10, min(100, (position // 10) * 10))
                
                return {
                    'trading_signal': signal,
                    'confidence_level': confidence,
                    'position_size': position
                }
                
            except (ValueError, TypeError) as e:
                print(f"Invalid numeric values: {e}")
                return None
        else:
            print(f"Invalid result format: {type(result)}")
            return None

    except Exception as e:
        print(f"Error generating trading signal for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return None


async def analyze_protfolio(
        symbol : str,
        tech_results : Optional[Dict[str,Any]] = None,
        data_collection_result : Optional[Dict[str,Any]] = None,
        news_data : Optional[Dict[str,Any]] = None,
        analysis_date : Optional[str] = None
) -> Dict[str,Any]:
    """
        Generate trading decision for a symbol based on technical and news data.
    
        Args:
            symbol: Stock symbol
            technical_data: Technical analysis from previous agent
            news_data: News intelligence from previous agent
            
        Returns:
            Dict with trading decision or error info
    """
    try:
        symbol = symbol.upper()

        # Validate and extract the actual data for symbol
        if not tech_results or not tech_results.get('success'):
            return {
                'symbol': symbol,
                'success': False,
                'error': 'No valid technical analysis data provided'
            }
        
        if not data_collection_result or not data_collection_result.get('success'):
            return{
                'symbol' : symbol,
                'success' : False,
                'error' : 'No valid companys data provided'
            }
        
        if not news_data or not news_data.get('success'):
            return {
                'symbol': symbol,
                'success': False,
                'error': 'No valid news intelligence data provided'
            }
        
        # pass only the relevant data
        trading_decision = await generate_trading_signal_with_prompts(
            symbol, 
            tech_results,
            data_collection_result,
            news_data,
            analysis_date
        )
        
        if trading_decision is None:
            return {
                'symbol': symbol,
                'success': False,
                'error': 'Trading signal generation failed'
            }

        return {
            'symbol': symbol,
            'trading_signal': trading_decision.get('trading_signal'),
            'confidence_level': trading_decision.get('confidence_level'),
            'position_size': trading_decision.get('position_size'),
            'success': True
        }
                
    except Exception as e:
        print(f"Error in protfolio analysis for {symbol}")
        return {
            'symbol' : symbol,
            'success' : False,
            'error' : str(e)
        }
    

async def protfolio_manager_agent_node(state:AgentState)->AgentState:
    """
        Portfolio Manager Agent node for the workflow.
    
        Args:
            state: Current state of the workflow
            
        Returns:
            Updated state with portfolio management results
    """
    try:
        symbol = state['symbol']
        analysis_date = state.get('analysis_date')

        # Get Data directly from the state
        tech_results = state.get('technical_analysis_results',{})
        news_results = state.get('news_intelligence_results',{})
        data_collection_results = state.get('data_collection_results',{})

        

        # Analysis protfolio 
        analysis_result = await analyze_protfolio(symbol,tech_results,data_collection_results,news_results,analysis_date)

        all_results = {symbol: analysis_result}
        
        # Update the main state with the results
        state['portfolio_manager_results'] = all_results
        state['current_step'] = 'portfolio_management_complete'

        if all_results.get('success'):
            state['error'] = "Protfolio Analysis Failed : {e}"
        
        return state

        
    except Exception as e:
        print(f"Error in portfolio_manager_agent_node: {e}")
        state['error'] = f"Portfolio Manager Agent failed: {e}"
        return state 