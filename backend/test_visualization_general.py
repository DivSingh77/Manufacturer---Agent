from app.response.visualization import build_visualization


def check(name, condition):

    if condition:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")

    assert condition, name


print("\nVISUALIZATION TESTS\n")


# =========================================================
# 1. Price history
# =========================================================

viz = build_visualization(
    intent="price_history",
    columns=[
        "placed_on",
        "unit_price",
    ],
    rows=[
        (
            "2026-08-01",
            15.5,
        ),
        (
            "2026-08-10",
            16.25,
        ),
    ],
)

check(
    "Price history creates line chart",
    viz is not None
    and viz["type"] == "line",
)

check(
    "Price history uses unit_price",
    viz["y_key"] == "unit_price",
)


# =========================================================
# 2. Stock by location
# =========================================================

viz = build_visualization(
    intent="current_stock",
    columns=[
        "location_name",
        "total_quantity",
    ],
    rows=[
        (
            "Warehouse A",
            120,
        ),
        (
            "Warehouse B",
            80,
        ),
    ],
)

check(
    "Stock by location creates bar chart",
    viz is not None
    and viz["type"] == "bar",
)

check(
    "Stock chart uses location",
    viz["x_key"] == "location_name",
)

check(
    "Stock chart uses quantity",
    viz["y_key"] == "total_quantity",
)


# =========================================================
# 3. Inventory movement
# =========================================================

viz = build_visualization(
    intent="inventory_movement",
    columns=[
        "transaction_date",
        "movement_quantity",
    ],
    rows=[
        (
            "2026-08-01",
            100,
        ),
        (
            "2026-08-02",
            -20,
        ),
        (
            "2026-08-03",
            50,
        ),
    ],
)

check(
    "Inventory movement creates line chart",
    viz is not None
    and viz["type"] == "line",
)


# =========================================================
# 4. Vendors by PO count
# =========================================================

viz = build_visualization(
    intent="vendor_analysis",
    columns=[
        "vendor_name",
        "purchase_order_count",
    ],
    rows=[
        (
            "Vendor A",
            10,
        ),
        (
            "Vendor B",
            6,
        ),
    ],
)

check(
    "Vendor comparison creates bar chart",
    viz is not None
    and viz["type"] == "bar",
)

check(
    "Vendor count uses correct metric",
    viz["y_key"]
    == "purchase_order_count",
)


# =========================================================
# 5. Vendor spend
# =========================================================

viz = build_visualization(
    intent="vendor_analysis",
    columns=[
        "vendor_name",
        "total_spend",
    ],
    rows=[
        (
            "Vendor A",
            250000,
        ),
        (
            "Vendor B",
            175000,
        ),
    ],
)

check(
    "Vendor spend creates bar chart",
    viz is not None
    and viz["type"] == "bar",
)

check(
    "Vendor spend title correct",
    viz["title"] == "Spend by Vendor",
)


# =========================================================
# 6. No meaningful chart
# =========================================================

viz = build_visualization(
    intent="purchase_order_details",
    columns=[
        "po_number",
        "status",
    ],
    rows=[
        (
            "PO-2026-0001",
            "placed",
        ),
    ],
)

check(
    "Non-chart data returns no visualization",
    viz is None,
)


print(
    "\nALL VISUALIZATION TESTS PASSED\n"
)