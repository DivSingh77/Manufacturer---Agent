from datetime import date, datetime
from decimal import Decimal


def make_json_safe(value):
    """
    Convert PostgreSQL/Python values into JSON-safe values.
    """

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


def rows_to_dicts(columns, rows):
    """
    Convert DB result rows into dictionaries.
    """

    result = []

    for row in rows:
        item = {}

        for column, value in zip(columns, row):
            item[column] = make_json_safe(value)

        result.append(item)

    return result


def find_first_key(columns, candidates):
    """
    Return the first matching column from a list
    of possible column names.
    """

    column_set = set(columns)

    for candidate in candidates:
        if candidate in column_set:
            return candidate

    return None


def build_visualization(
    intent,
    columns,
    rows,
):
    """
    Build visualization metadata when the query result
    is suitable for a chart.

    Visualization decisions use both:
    1. business intent
    2. actual returned column names

    This avoids depending on one exact SQL alias.
    """

    if not columns or not rows:
        return None

    data = rows_to_dicts(
        columns,
        rows,
    )

    # =========================================================
    # Candidate column groups
    # =========================================================

    date_key = find_first_key(
        columns,
        [
            "placed_on",
            "received_at",
            "transaction_date",
            "transaction_at",
            "created_at",
            "date",
            "month",
            "day",
        ],
    )

    price_key = find_first_key(
        columns,
        [
            "unit_price",
            "price",
            "unit_cost",
            "average_price",
            "avg_price",
        ],
    )

    location_key = find_first_key(
        columns,
        [
            "location_name",
            "location",
            "warehouse_name",
            "warehouse",
        ],
    )

    stock_key = find_first_key(
        columns,
        [
            "total_quantity",
            "total_stock",
            "stock_quantity",
            "quantity",
            "current_stock",
        ],
    )

    vendor_key = find_first_key(
        columns,
        [
            "vendor_name",
            "vendor",
            "supplier_name",
            "supplier",
        ],
    )

    vendor_metric_key = find_first_key(
        columns,
        [
            "purchase_order_count",
            "po_count",
            "order_count",
            "total_orders",
            "total_spend",
            "purchase_value",
        ],
    )

    movement_key = find_first_key(
        columns,
        [
            "movement_quantity",
            "net_quantity",
            "transaction_quantity",
            "quantity",
            "total_quantity",
        ],
    )

    item_key = find_first_key(
        columns,
        [
            "item_name",
            "name",
            "item",
        ],
    )

    count_key = find_first_key(
        columns,
        [
            "count",
            "transaction_count",
            "purchase_count",
            "order_count",
            "purchase_order_count",
        ],
    )

    # =========================================================
    # 1. Purchase price history
    # =========================================================

    if (
        intent == "price_history"
        and date_key
        and price_key
    ):
        sorted_data = sorted(
            data,
            key=lambda item: str(
                item.get(date_key, "")
            ),
        )

        return {
            "type": "line",
            "title": "Purchase Price History",
            "x_key": date_key,
            "y_key": price_key,
            "data": sorted_data,
        }

    # =========================================================
    # 2. Stock by warehouse/location
    # =========================================================

    if (
        location_key
        and stock_key
        and intent
        in {
            "current_stock",
            "stock_by_location",
            "inventory_analysis",
        }
    ):
        return {
            "type": "bar",
            "title": "Stock by Location",
            "x_key": location_key,
            "y_key": stock_key,
            "data": data,
        }

    # =========================================================
    # 3. Inventory movement over time
    # =========================================================

    if (
        date_key
        and movement_key
        and intent
        in {
            "inventory_movement",
            "inventory_transactions",
            "transaction_history",
            "stock_movement",
        }
    ):
        sorted_data = sorted(
            data,
            key=lambda item: str(
                item.get(date_key, "")
            ),
        )

        return {
            "type": "line",
            "title": "Inventory Movement Over Time",
            "x_key": date_key,
            "y_key": movement_key,
            "data": sorted_data,
        }

    # =========================================================
    # 4. Vendor comparison
    # =========================================================

    if (
        vendor_key
        and vendor_metric_key
    ):
        title = "Vendor Comparison"

        if vendor_metric_key in {
            "total_spend",
            "purchase_value",
        }:
            title = "Spend by Vendor"

        elif vendor_metric_key in {
            "purchase_order_count",
            "po_count",
            "order_count",
            "total_orders",
        }:
            title = "Purchase Orders by Vendor"

        return {
            "type": "bar",
            "title": title,
            "x_key": vendor_key,
            "y_key": vendor_metric_key,
            "data": data,
        }

    # =========================================================
    # 5. Item frequency / ranking
    # =========================================================

    if (
        item_key
        and count_key
        and intent
        in {
            "purchase_frequency",
            "item_analysis",
            "inventory_analysis",
        }
    ):
        return {
            "type": "bar",
            "title": "Item Frequency",
            "x_key": item_key,
            "y_key": count_key,
            "data": data,
        }

    # =========================================================
    # 6. Generic time-series fallback
    # =========================================================

    if date_key:

        numeric_candidates = []

        for column in columns:

            if column == date_key:
                continue

            values = [
                row.get(column)
                for row in data
                if row.get(column) is not None
            ]

            if not values:
                continue

            if all(
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                for value in values
            ):
                numeric_candidates.append(
                    column
                )

        if numeric_candidates:

            y_key = numeric_candidates[0]

            sorted_data = sorted(
                data,
                key=lambda item: str(
                    item.get(date_key, "")
                ),
            )

            return {
                "type": "line",
                "title": "Trend Over Time",
                "x_key": date_key,
                "y_key": y_key,
                "data": sorted_data,
            }

    # =========================================================
    # No meaningful visualization
    # =========================================================

    return None