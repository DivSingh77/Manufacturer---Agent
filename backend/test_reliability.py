from unittest.mock import patch

from app.agent.nodes.execute_sql import execute_sql_node
from app.agent.nodes.query_failure import query_failure_node


def check(name, condition):

    if condition:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")

    assert condition, name


print("\nRELIABILITY TESTS\n")


# =========================================================
# 1. Runtime SQL error gets captured
# =========================================================

state = {
    "sql": (
        "SELECT definitely_invalid_column "
        "FROM inv_items"
    )
}

with patch(
    "app.agent.nodes.execute_sql.execute_query",
    side_effect=Exception(
        'column "definitely_invalid_column" does not exist'
    ),
):

    result = execute_sql_node(state)


check(
    "Runtime DB exception captured",
    bool(result.get("execution_error")),
)

check(
    "Runtime DB exception does not become user-facing error",
    "error" not in result,
)

check(
    "Failed query returns empty rows",
    result.get("result_rows") == [],
)


# =========================================================
# 2. Retry exhaustion returns safe answer
# =========================================================

state = {
    "execution_error": (
        'column "secret_internal_column" does not exist'
    ),
    "retry_count": 2,
}

result = query_failure_node(state)

answer = result.get(
    "answer",
    "",
)


check(
    "Retry exhaustion returns an answer",
    bool(answer),
)

check(
    "Raw database error is not exposed",
    "secret_internal_column"
    not in answer,
)


# =========================================================
# 3. Failure state has no query data
# =========================================================

check(
    "Failure returns empty result rows",
    result.get("result_rows") == [],
)

check(
    "Failure returns no visualization",
    result.get("visualization") is None,
)


print(
    "\nALL RELIABILITY TESTS PASSED\n"
)