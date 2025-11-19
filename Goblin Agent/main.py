import sys
from datetime import datetime
from pathlib import Path
import asyncio
import warnings

# Add the project root to the python path
project_root = Path(__file__).parent
sys.path.insert(0,str(project_root))

from src.workflows.workflow import run_analysis

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Goblin Agent"

def print_workflow_summary(result : str , date : str) -> None:
    """print summary of workflow result for current date"""
    if not result.get('success'):
        print(f"{date} Analysis Failed. {result.get('error','Unkown error')}")
        return


def _prompt(prompt : str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""
    

def prompt_symbol()->str:
    """Prompt the user for a stock symbol 

        Return symbol  
    """
    
    # Symbol
    while True:
        sym = _prompt("Enter a stock symbol like (AAPL) :").strip().upper()
        if sym:
            break
        print("symbol cannot be empty")

    return sym


async def main():
    """Main execution with interactive symbol"""

    try:
        print("Goblin - Financial Ananlysis Agent")
        print(f"\n")
        print("="*80)

        # interactive input
        symbol = prompt_symbol()
        analysis_date = datetime.today().date().strftime("%Y-%m-%d")
        print(f"Symbol: {symbol}")
        print(f"Current  date: {analysis_date}")
        print(f"Starting workflow execution...")
        print(f"\n")
        print("="*80)
        
        
        date_formatted = datetime.now()
        session_id = f"daily_analysis{date_formatted}"  
        warnings.filterwarnings("ignore", message=".*UUID v7.*")   

        try:
            # execut workflow for this date
            result = await run_analysis(symbol,analysis_date,session_id)  

            # print workflow summary
            print_workflow_summary(result,analysis_date)

        except Exception as e:
                print(f"{analysis_date} execution error : {e}")

        # Final Summary
        print(f"\nANALYSIS COMPLETE")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    
    except Exception as e:
        print(f"Main execution error : {e}")


if __name__ == "__main__":
    asyncio.run(main()) 