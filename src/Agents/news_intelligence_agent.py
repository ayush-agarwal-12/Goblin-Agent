from ..workflows.state import AgentState
from typing import Optional,Dict,Any
from ..tools.finnhub_tool import get_company_news
from typing import List
import os,json
from langchain_groq import ChatGroq
from ..prompts.prompts import news_feature_analyze_template

async def extract_nlp_features(symbol: str, news_result: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Extract NLP features from news result"""
    api_key = os.getenv('GROQ_API_KEY')

    if not api_key:
        print(f"No Groq API key available for {symbol}")
        return None
    
    llm = ChatGroq(
        model='llama-3.3-70b-versatile', 
        api_key=api_key, 
        temperature=0.2,
        max_tokens=1000
    )
    prompt_template = news_feature_analyze_template()

    nlp_features = []
    
    limited_news = news_result[:3]
    print(f"Processing {len(limited_news)} articles for {symbol}\n")

    for idx, article in enumerate(limited_news, 1):
        
        print(f"Processing article {idx}/{len(limited_news)}")
        
        
        try:
            prompt = prompt_template.format(**article)
            
            response = await llm.ainvoke(prompt)
            content = response.content.strip()
            
            print(content)
            print(f"\n\n")

            # Try to parse the JSON
            data = None
            
            # Method 1: Extract from ```json blocks
            if "```json" in content:
                # print("Found ```json block")
                start = content.find("```json") + 7
                end = content.find("```", start)
                
                if end == -1:
                    print("WARNING: No closing ``` found, using rest of content")
                    json_str = content[start:].strip()
                else:
                    json_str = content[start:end].strip()
                
                print(f"Extracted JSON string (length {len(json_str)}):")
                print(json_str)
                
                try:
                    data = json.loads(json_str)
                    print("✓ Successfully parsed JSON from code block")
                except json.JSONDecodeError as e:
                    print(f"✗ JSON parse error: {e}")
                    print(f"Error at position {e.pos}")
            
            # Method 2: Extract from regular ``` blocks
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                
                if end == -1:
                    json_str = content[start:].strip()
                else:
                    json_str = content[start:end].strip()
                
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"✗ JSON parse error: {e}")
            
            # Method 3: Try direct parsing
            else:
                print("No code blocks found, trying direct parse")
                try:
                    data = json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"✗ Direct JSON parse failed: {e}")
            
            if data:
                nlp_features.append(data)
                print(f"✓ Article {idx} successfully processed\n")
            else:
                print(f"✗ Article {idx} failed - no valid JSON extracted\n")
        
        except Exception as e:
            print(f"ERROR processing article {idx}: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\n")
    print(f"SUMMARY: Extracted {len(nlp_features)} features from {len(limited_news)} articles")
    print(f"\n")

    if not nlp_features:
        return None
    
    return {
        'news_features': nlp_features,
        'total_analyzed': len(nlp_features)
    }

    
async def analyze_news(symbol:str,analysis_date : str)->Dict[str,Any]:
    """
        Complete news analysis with PrimoGPT workflow:
        1. Get news -> 2. Sample random articles -> 3. Assess significance 
        4. Scrape significant articles -> 5. Generate NLP features
    """
    try:
        symbol = symbol.upper()
        
        # 1. Get news data for analysis
        news_result = await get_company_news(symbol, analysis_date)

        if not news_result or not news_result.success:
            return {
                'symbol' : symbol,
                'success' : False,
                'error' : f"No news data found for {symbol}"
            }
        
        news_result = news_result.data
        
        news = news_result.get('news',[])
        total_news = news_result.get('total_count',0)

        nlp_features = await extract_nlp_features(symbol,news)

        if not nlp_features:
            return {
                'symbol': symbol,
                'success': False,
                'error': 'NLP feature extraction failed'
            }
        
        return {
            'symbol': symbol,
            'success': True,
            'nlp_features': nlp_features,
            'total_news' : total_news
        }

    except Exception as e:
        print(f"Error in news analysis for {symbol}: {e}")
        return {
            'symbol': symbol,
            'success': False,
            'error': str(e)
        }

async def news_intelligence_agent_node(state : AgentState) -> AgentState:
    """
        LangGraph node for news intelligence.
    """

    try:
        # Get Symbol,analysis_dateand technical_data
        symbol = state['symbol']
        analysis_date = state['analysis_date']


        # Perform complete news analysis with company context
        result = await analyze_news(symbol, analysis_date)
        
        # Update state
        state['news_intelligence_results'] = result
        state['current_step'] = 'news_intelligence_complete'
        
        if not result['success']:
            state['error'] = result.get('error', 'News intelligence failed')
            
        return state
        
    except Exception as e:
        print(f"News intelligence node error: {e}")
        state['error'] = str(e)
        state['current_step'] = 'error'
        return state 