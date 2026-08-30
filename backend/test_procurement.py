from app.agent.graph import agent_graph

TESTS = [
    {
        "persona": "procurement",
        "question": "Show me all placed purchase orders.",
    },
    {
        "persona": "procurement",
        "question": "Which purchase orders are partially received?",
    },
    {
        "persona": "procurement",
        "question": "Which vendors have the most purchase orders?",
    },
    {
        "persona": "procurement",
        "question": "Show details of PO-2026-0029 including vendor and items.",
    },
    {
        "persona": "procurement",
        "question": "Show receipts for PO-2026-0029.",
    },
    {
        "persona": "procurement",
        "question": "Which items have been purchased most frequently?",
    },
]


for test in TESTS:

    print("\n" + "=" * 80)
    print(f"PERSONA: {test['persona']}")
    print(f"QUESTION: {test['question']}")
    print("=" * 80)

    try:

        result = agent_graph.invoke(
            {
                "question": test["question"],
                "persona": test["persona"],
                "retry_count": 0,
            }
        )

        print("\nDOMAIN:")
        print(result.get("domain"))

        print("\nINTENT:")
        print(result.get("intent"))

        print("\nERROR:")
        print(result.get("error"))

        print("\nSQL:")
        print(result.get("sql"))

        print("\nSQL VALID:")
        print(result.get("sql_valid"))

        print("\nVALIDATION ERROR:")
        print(result.get("validation_error"))

        print("\nANSWER:")
        print(result.get("answer"))

    except Exception as e:

        print("\nEXCEPTION:")
        print(type(e).__name__)
        print(str(e))