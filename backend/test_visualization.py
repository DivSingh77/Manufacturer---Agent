from app.agent.graph import agent_graph

result = agent_graph.invoke(
    {
        "question": (
            "Show the purchase price history of "
            "MS C Channel – 125×65×5mm."
        ),
        "persona": "procurement",
        "retry_count": 0,
    }
)


print("\nDOMAIN:")
print(result.get("domain"))

print("\nINTENT:")
print(result.get("intent"))

print("\nSQL:")
print(result.get("sql"))

print("\nSQL VALID:")
print(result.get("sql_valid"))

print("\nANSWER:")
print(result.get("answer"))

print("\nVISUALIZATION:")
print(result.get("visualization"))