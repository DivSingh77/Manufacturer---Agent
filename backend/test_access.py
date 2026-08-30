from app.agent.graph import agent_graph

TESTS = [
    # Warehouse should NOT access procurement
    {
        "persona": "warehouse",
        "question": "Show me all purchase orders.",
    },

    # Procurement should access procurement
    {
        "persona": "procurement",
        "question": "Show me all purchase orders.",
    },

    # Procurement should NOT perform stock analysis
    {
        "persona": "procurement",
        "question": "What is the current stock of all items?",
    },

    # Owner should access procurement
    {
        "persona": "owner",
        "question": "Show me all purchase orders.",
    },

    # Owner should access inventory
    {
        "persona": "owner",
        "question": "What is the current stock of all items?",
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

        print("\nALLOWED TABLES:")
        print(result.get("allowed_tables"))

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