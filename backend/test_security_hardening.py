from app.agent.graph import agent_graph
from app.sql.validator import validate_sql


def assert_test(name, condition):

    if condition:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")

    assert condition, name


print("\nSECURITY HARDENING TESTS\n")


# ==========================================================
# 1. Comma join bypass
# ==========================================================

sql = """
SELECT *
FROM inv_items i, proc_purchase_orders p
WHERE i.id = p.vendor_id
"""

valid, message = validate_sql(
    sql,
    "warehouse",
)

assert_test(
    "Warehouse comma-join attack blocked",
    valid is False,
)


# ==========================================================
# 2. Explicit JOIN
# ==========================================================

sql = """
SELECT *
FROM inv_items i
JOIN proc_purchase_orders p
    ON i.id = p.vendor_id
"""

valid, message = validate_sql(
    sql,
    "warehouse",
)

assert_test(
    "Warehouse explicit procurement JOIN blocked",
    valid is False,
)


# ==========================================================
# 3. Nested subquery bypass
# ==========================================================

sql = """
SELECT *
FROM inv_items
WHERE id IN (
    SELECT inv_item_id
    FROM proc_po_lines
)
"""

valid, message = validate_sql(
    sql,
    "warehouse",
)

assert_test(
    "Warehouse nested procurement subquery blocked",
    valid is False,
)


# ==========================================================
# 4. Warehouse legitimate query
# ==========================================================

sql = """
SELECT i.name, cs.quantity
FROM inv_items i
JOIN inv_current_stock cs
    ON cs.item_id = i.id
"""

valid, message = validate_sql(
    sql,
    "warehouse",
)

assert_test(
    "Warehouse legitimate inventory query allowed",
    valid is True,
)


# ==========================================================
# 5. Procurement stock analysis blocked at graph level
# ==========================================================

result = agent_graph.invoke(
    {
        "question": (
            "What is the current stock "
            "of all inventory items?"
        ),
        "persona": "procurement",
    }
)

assert_test(
    "Procurement inventory analysis denied",
    bool(result.get("error")),
)

assert_test(
    "Denied procurement request generated no SQL",
    not result.get("sql"),
)


# ==========================================================
# 6. Warehouse cross-domain question
# ==========================================================

result = agent_graph.invoke(
    {
        "question": (
            "For PO-2026-0029, compare the ordered "
            "quantity with current warehouse stock."
        ),
        "persona": "warehouse",
    }
)

print(
    "Warehouse cross-domain classification:",
    result.get("domain"),
)

assert_test(
    "Warehouse cross-domain request denied",
    bool(result.get("error")),
)


# ==========================================================
# 7. Owner cross-domain allowed
# ==========================================================

result = agent_graph.invoke(
    {
        "question": (
            "For PO-2026-0029, compare what was "
            "ordered with what is currently in stock."
        ),
        "persona": "owner",
    }
)

print(
    "Owner domain:",
    result.get("domain"),
)

assert_test(
    "Owner cross-domain request allowed",
    not result.get("error"),
)


print("\nALL SECURITY TESTS PASSED\n")