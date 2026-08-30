from app.agent.graph import agent_graph

TESTS = [
    {
        "name": "Warehouse inventory allowed",
        "persona": "warehouse",
        "question": "Which items currently have zero stock?",
        "expected_domain": "inventory",
        "should_have_sql": True,
        "should_be_denied": False,
    },
    {
        "name": "Warehouse procurement denied",
        "persona": "warehouse",
        "question": "Show me all purchase orders.",
        "expected_domain": "procurement",
        "should_have_sql": False,
        "should_be_denied": True,
    },
    {
        "name": "Procurement PO access",
        "persona": "procurement",
        "question": "Which purchase orders are partially received?",
        "expected_domain": "procurement",
        "should_have_sql": True,
        "should_be_denied": False,
    },
    {
        "name": "Procurement inventory denied",
        "persona": "procurement",
        "question": "What is the current stock of all items?",
        "expected_domain": "inventory",
        "should_have_sql": False,
        "should_be_denied": True,
    },
    {
        "name": "Owner inventory allowed",
        "persona": "owner",
        "question": "What is the current stock of all items?",
        "expected_domain": "inventory",
        "should_have_sql": True,
        "should_be_denied": False,
    },
    {
        "name": "PO detail multi-table join",
        "persona": "procurement",
        "question": "Show details of PO-2026-0029 including vendor and items.",
        "expected_domain": "procurement",
        "should_have_sql": True,
        "should_be_denied": False,
    },
    {
        "name": "Receipt join",
        "persona": "procurement",
        "question": "Show receipts for PO-2026-0029.",
        "expected_domain": "procurement",
        "should_have_sql": True,
        "should_be_denied": False,
    },
    {
        "name": "Price history visualization",
        "persona": "procurement",
        "question": (
            "Show the purchase price history of "
            "MS C Channel – 125×65×5mm."
        ),
        "expected_domain": "procurement",
        "should_have_sql": True,
        "should_be_denied": False,
        "expected_visualization": "line",
    },
]


passed = 0
failed = 0


for test in TESTS:

    print("\n" + "=" * 80)
    print(test["name"])
    print("=" * 80)

    try:

        result = agent_graph.invoke(
            {
                "question": test["question"],
                "persona": test["persona"],
                "retry_count": 0,
            }
        )

        checks = []

        # Domain
        checks.append(
            (
                result.get("domain")
                == test["expected_domain"],
                f"domain = {result.get('domain')}",
            )
        )

        # SQL presence
        if test["should_have_sql"]:
            checks.append(
                (
                    bool(result.get("sql")),
                    "SQL generated",
                )
            )
        else:
            checks.append(
                (
                    not result.get("sql"),
                    "SQL not generated",
                )
            )

        # Access denial
        answer = result.get("answer") or ""

        denied = answer.lower().startswith(
            "access denied"
        )

        checks.append(
            (
                denied == test["should_be_denied"],
                f"access denied = {denied}",
            )
        )

        # SQL validation
        if test["should_have_sql"]:
            checks.append(
                (
                    result.get("sql_valid") is True,
                    f"sql_valid = {result.get('sql_valid')}",
                )
            )

        # Visualization
        if "expected_visualization" in test:

            viz = result.get("visualization")

            checks.append(
                (
                    viz is not None
                    and viz.get("type")
                    == test["expected_visualization"],
                    f"visualization = {viz}",
                )
            )

        all_passed = all(
            status for status, _ in checks
        )

        for status, message in checks:

            symbol = "PASS" if status else "FAIL"

            print(f"[{symbol}] {message}")

        if all_passed:
            passed += 1
            print("\nRESULT: PASS")
        else:
            failed += 1
            print("\nRESULT: FAIL")

    except Exception as e:

        failed += 1

        print(
            f"\nRESULT: FAIL - "
            f"{type(e).__name__}: {e}"
        )


print("\n" + "=" * 80)
print("EVALUATION SUMMARY")
print("=" * 80)

print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total:  {len(TESTS)}")

score = (
    passed / len(TESTS) * 100
    if TESTS
    else 0
)

print(f"Score:  {score:.1f}%")