from langchain_core.prompts import ChatPromptTemplate
# from langchain.output_parsers import StructuredOutputParser, ResponseSchema

def news_feature_analyze_template()->ChatPromptTemplate:
    """Prompt template to extract key features from news result"""
    template = """
                You are a Financial News Feature Extraction Agent.

                    Your job is to read the following news article and extract only the most important
                    key features that impact the stock's price, future outlook, or risk level.

                    Follow these rules strictly:
                    - Be concise and factual.
                    - Do NOT rewrite the full article.
                    - No long paragraphs.
                    - No filler text.
                    - Only extract signals relevant to stock investors.
                    - If information is missing, return "N/A".

                    News Article:
                    ------------------
                    Headline: {headline}
                    Summary: {summary}
                    Source: {source}
                    URL: {url}
                    ------------------

                    Return output as a JSON object with these fields:

                    {{
                        "headline": "",
                        "published_date": "",
                        "source": "",
                        "key_points": [
                            "Main point 1",
                            "Main point 2",
                            "Main point 3"
                        ],
                        "sentiment": "positive | negative | neutral",
                        "impact": "high | medium | low",
                        "category": "earnings | product | regulatory | litigation | macro | management | competitive | analyst_ratings | supply_chain | other"
                    }}
                """
    return ChatPromptTemplate.from_template(template)


def get_portfolio_manager_template() -> ChatPromptTemplate:
    """
    Portfolio Manager with balanced decision-making focused on actionable signals.
    """
    template = """You are an aggressive quantitative portfolio manager making decisive trading decisions.

                [ANALYSIS DATE: {analysis_date}]
                [SYMBOL: {symbol}]
                [CURRENT PRICE: ${current_price}]

                [COMPANY PROFILE]
                {company_profile}

                [TECHNICAL INDICATORS]
                {sma}
                {ema}

                [FUNDAMENTAL METRICS]
                {financials}

                [NEWS SENTIMENT & KEY DEVELOPMENTS]
                {news}

                [RECENT PRICE ACTION]
                {history}

                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                [TRADING DECISION FRAMEWORK]

                Your goal: Maximize returns by identifying directional price movements. Missing opportunities costs as much as wrong trades.

                SIGNAL DEFINITIONS:
                → BUY: Expect upward price movement. Use when technical momentum is positive OR news is bullish with neutral technicals.
                → SELL: Expect downward price movement. Use when technical momentum is negative OR news is bearish with neutral technicals.
                → HOLD: Use ONLY when data is genuinely contradictory or insufficient (target: <15% of all decisions).

                TECHNICAL ANALYSIS PRIORITY:
                1. RSI Signals {rsi}:
                - RSI < 40: Oversold → lean BUY (unless strong negative news)
                - RSI 40-60: Neutral → follow news sentiment and MACD
                - RSI > 60: Overbought → lean SELL (unless strong positive news)

                2. MACD Momentum {macd}:
                - Positive histogram: Bullish momentum → favor BUY
                - Negative histogram: Bearish momentum → favor SELL
                - Near zero: Follow news sentiment and price trends

                3. Moving Averages (SMA/EMA){moving_average}:
                - Price > SMA: Uptrend → favor BUY
                - Price < SMA: Downtrend → favor SELL

                4.Bollinger Bands: {bbands}
                - Volatility bands around moving average
                - Price position relative to bands indicates volatility and potential reversal points

                5.ADX (Average Directional Index): {adx}
                - Measures trend strength regardless of direction
                - Higher values indicate stronger trends

                6.CCI (Commodity Channel Index): {cci}
                - Measures cyclical trends and momentum
                - Values above +100 or below -100 indicate strong momentum conditions

                NEWS INTEGRATION:
                - Positive sentiment + neutral/bullish technicals = BUY
                - Negative sentiment + neutral/bearish technicals = SELL
                - News confirms technical signals = HIGH CONFIDENCE
                - News contradicts technical signals = Reduce position size, don't default to HOLD

                DECISION EXAMPLES:
                ✓ RSI=45, MACD positive, positive news → BUY (60-80% position)
                ✓ RSI=55, MACD negative, negative news → SELL (60-80% position)
                ✓ RSI=35, MACD negative, positive news → BUY (30-40% position, conflict)
                ✓ RSI=65, MACD positive, negative news → SELL (30-40% position, conflict)
                ✗ RSI=50, MACD near 0, neutral news → HOLD (only if truly ambiguous)

                POSITION SIZING:
                - Strong alignment (tech + news): 60-100%
                - Moderate signals: 40-60%
                - Conflicting signals: 20-40%
                - Weak/unclear signals: 10-20%

                CONFIDENCE LEVELS:
                - 0.8-1.0: All indicators strongly aligned
                - 0.6-0.7: Most indicators aligned, minor conflicts
                - 0.4-0.5: Mixed signals but direction identifiable
                - 0.2-0.3: Weak signals, low conviction
                - 0.1: Truly ambiguous (rare, use HOLD)

                ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                [CRITICAL REQUIREMENTS]
                1. Be DECISIVE - HOLD should be rare (<15% of cases)
                2. Weight technicals heavily - they predict short-term moves
                3. News adds conviction - use it to adjust position size and confidence
                4. When uncertain between BUY/SELL, choose based on dominant signal
                5. Return ONLY valid JSON with exact lowercase keys using underscores

                [OUTPUT FORMAT]
                Return ONLY this JSON (no markdown, no extra text):
                {{
                    "trading_signal": "BUY",
                    "confidence_level": 0.7,
                    "position_size": 60
                }}

                Valid signals: BUY, SELL, HOLD
                Valid confidence: 0.1 to 1.0 (steps of 0.1)
                Valid position: 10 to 100 (steps of 10)
                """

    return ChatPromptTemplate.from_template(template)


# def get_structured_output_parser():
#     """
#     Creates a structured output parser for portfolio manager decisions.
#     """
#     response_schemas = [
#         ResponseSchema(
#             name="trading_signal",
#             description="The recommended trading action: BUY, SELL, or HOLD"
#         ),
#         ResponseSchema(
#             name="confidence_level",
#             description="Confidence level in the decision (0.1-1.0)"
#         ),
#         ResponseSchema(
#             name="position_size",
#             description="Recommended position size as percentage (10-100)"
#         )
#     ]
    
#     return StructuredOutputParser.from_response_schemas(response_schemas)