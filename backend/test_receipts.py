from app.agent.graph import agent_graph

result = agent_graph.invoke(
    {
        "question": "Show receipts for PO-2026-0029.",
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

print("\nVALIDATION ERROR:")
print(result.get("validation_error"))

print("\nANSWER:")
print(result.get("answer"))