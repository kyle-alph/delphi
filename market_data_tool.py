import os
from massive import RESTClient

TOOL_DEF = {
    "name": "get_stock_prices",
    "description": "Retireves historical OHLCV price data for a stock ticker given a date range.",
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": { "type": "string" },
            "multiplier": {"type": "integer" },
            "from_date": { "type": "string" },
            "to_date": { "type": "string" },
            "time_interval": { "type": "string", "enum": ["minute", "hour", "day", "week"] },
            "limit": { "type": "integer" },
        },
        "required": [
            "ticker", "from_date", "to_date",
        ]
    }
}

def run(ticker: str, multiplier: int, from_date: str, to_date: str, time_interval: str = "day", limit: int = 50):
    client = RESTClient(api_key=os.environ["MASSIVE_API_KEY"])
    return client.get_aggs(
        ticker=ticker,
        multiplier=multiplier,
        from_=from_date,
        to=to_date,
        timespan=time_interval,
        limit=limit
    )
