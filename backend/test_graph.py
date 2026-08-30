from app.agent.graph import agent_graph

if __name__ == "__main__":

    result = agent_graph.invoke(
        {
            "question": "What is the current stock of all items?",
            "persona": "warehouse",
        }
    )

    print("\n" + "=" * 80)
    print("FINAL ANSWER")
    print("=" * 80)

    print(result.get("answer"))

    print("\n" + "=" * 80)
    print("GENERATED SQL")
    print("=" * 80)

    print(result.get("sql"))

    print("\n" + "=" * 80)
    print("INTENT")
    print("=" * 80)

    print(result.get("intent"))

    print("\n" + "=" * 80)
    print("DOMAIN")
    print("=" * 80)

    print(result.get("domain"))