import sys, json
import anthropic
import market_data_tool
import options_data_tool

client = anthropic.Anthropic()

TOOLS = [
    market_data_tool.TOOL_DEF,
    options_data_tool.TOOL_DEF
]

TOOL_RUNNERS = {
    "get_stock_prices": market_data_tool.run,
    "get_option_data": options_data_tool.run
}

response = client.messages.create(
    model = "claude-sonnet-4-6",
    max_tokens = 1024,
    tools = TOOLS,
    tool_choice = { "type": "auto", "disable_parallel_tool_use": True },
    messages = [
        {
            "role": "user",
            "content": " ".join(sys.argv[1:]),
        },
    ],
)

print(f"stop_reason: {response.stop_reason}")

if response.stop_reason == "end_turn":
    final_text = next(block for block in response.content if block.type == "text")
    print(final_text.text)
    sys.exit(0)

tool_use = next(a for a in response.content if a.type == "tool_use")
print(f"Tool: {tool_use.name}")
print(f"Input: {tool_use.input}")

result = TOOL_RUNNERS[tool_use.name](**tool_use.input)

followup = client.messages.create(
    model = "claude-sonnet-4-6",
    max_tokens = 1024,
    tools = TOOLS,
    tool_choice = {"type": "auto", "disable_parallel_tool_use": True},
    messages = [
        {
            "role": "user",
            "content": " ".join(sys.argv[1:]),
        },
        {
            "role": "assistant",
            "content": response.content,
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result, default = str),
                }
            ],
        },
    ]
)

final_text = next(block for block in followup.content if block.type == "text")
print(final_text)
