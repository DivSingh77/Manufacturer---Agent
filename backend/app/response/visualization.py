from datetime import date, datetime
from decimal import Decimal


def make_json_safe(value):

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    return value


def rows_to_dicts(columns, rows):

    return [
        {
            column: make_json_safe(value)
            for column, value in zip(columns, row)
        }
        for row in rows
    ]


def build_visualization(state):

    intent = state.get("intent")
    columns = state.get("result_columns", [])
    rows = state.get("result_rows", [])

    if not rows:
        return None

    data = rows_to_dicts(columns, rows)

    # ---------------------------------------
    # Purchase price history
    # ---------------------------------------

    if intent == "price_history":

        possible_date_keys = [
            "placed_on",
            "received_at",
            "created_at",
            "date",
        ]

        possible_price_keys = [
            "unit_price",
            "price",
            "unit_cost",
        ]

        x_key = next(
            (
                key
                for key in possible_date_keys
                if key in columns
            ),
            None,
        )

        y_key = next(
            (
                key
                for key in possible_price_keys
                if key in columns
            ),
            None,
        )

        if x_key and y_key:

            # Charts should run oldest -> newest
            data = sorted(
                data,
                key=lambda row: row.get(x_key) or "",
            )

            return {
                "type": "line",
                "title": "Purchase Price History",
                "x_key": x_key,
                "y_key": y_key,
                "data": data,
            }

    # ---------------------------------------
    # Vendor analysis
    # ---------------------------------------

    if intent == "vendor_analysis":

        if (
            "vendor_name" in columns
            and "purchase_order_count" in columns
        ):
            return {
                "type": "bar",
                "title": "Purchase Orders by Vendor",
                "x_key": "vendor_name",
                "y_key": "purchase_order_count",
                "data": data,
            }

    return None