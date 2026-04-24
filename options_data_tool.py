import os
import itertools
from massive import RESTClient

TOOL_DEF = {
    "name": "get_option_data",
    "description": "Retrieves option contracts for a given ticker including strike price, expiration date, and contract type. Use when the user asks about available options with an expiration date",
    "input_schema": {
        "type": "object",
        "properties": {
            "underlying_ticker": { "type": "string" },
            "contract_type": { "type": "string", "enum": ["call", "put"] },
            "expiration_date": {
                "type": "string",
                "description": "YYYY-MM-DD format"
            },
            "order": { "type": "string", "enum": ["asc", "desc"] },
            "limit": { "type": "integer" },
            "sort": { "type": "string", "enum": ["underlying_ticker", "expiration_date"] },
        },
        "required": [
            "underlying_ticker", "contract_type", "expiration_date"
        ]
    }
}

def run(underlying_ticker: str, contract_type: str, expiration_date: str, order: str = "asc", limit: int = 10, sort: str = "underlying_ticker"):
    client = RESTClient(api_key=os.environ["MASSIVE_API_KEY"])
    contracts = client.list_options_contracts(
        underlying_ticker=underlying_ticker,
        contract_type=contract_type,
        expiration_date=expiration_date,
        order=order,
        limit=limit,
        sort=sort
    )
    return list(itertools.islice(contracts, limit))
