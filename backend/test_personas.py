from app.agent.graph import agent_graph

TEST_CASES = [
    {
        "persona": "warehouse",
        "question": "What is the current stock of all items?",
    },
    {
        "persona": "warehouse",
        "question": "Which items currently have zero stock?",
    },
    {
        "persona": "warehouse",
        "question": "Show me the current stock by warehouse location.",
    },
    {
        "persona": "warehouse",
        "question": "Show me the recent inventory transactions.",
    },
]


for test in TEST_CASES:

    print("\n" + "=" * 80)
    print("PERSONA:", test["persona"])
    print("QUESTION:", test["question"])
    print("=" * 80)

    try:

        result = agent_graph.invoke(
            {
                "question": test["question"],
                "persona": test["persona"],
                "retry_count": 0,
            }
        )

        print("\nINTENT:")
        print(result.get("intent"))

        print("\nDOMAIN:")
        print(result.get("domain"))

        print("\nSQL:")
        print(result.get("sql"))

        print("\nANSWER:")
        print(result.get("answer"))

    except Exception as e:

        print("\nERROR:")
        print(e)