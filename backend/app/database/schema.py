from app.database.connection import get_connection

# ============================================================
# TABLE DESCRIPTIONS
# ============================================================

TABLE_DESCRIPTIONS = {
    # -------------------------
    # INVENTORY
    # -------------------------
    "inv_items": "Master list of inventory items.",

    "inv_categories": "Top-level inventory categories.",

    "inv_sub_categories": (
        "Inventory subcategories belonging to an inventory category."
    ),

    "inv_sub_categories_2": (
        "Second-level inventory subcategory. "
        "Contains fabrication-specific fields such as "
        "cut_shape, cut_formula and nomenclature_fields."
    ),

    "inv_locations": (
        "Warehouse/storage locations where inventory is held."
    ),

    "inv_current_stock": (
        "Current quantity of an inventory item at a particular location."
    ),

    "inv_issued_to_targets": (
        "Destinations to which inventory can be issued."
    ),

    "inv_transactions": (
        "Inventory movement ledger. "
        "Records inbound, outbound, transfer-in and transfer-out movements."
    ),

    "inv_field_definitions": (
        "Likely legacy/custom field definition table. "
        "Excluded from active agent scope."
    ),

    # -------------------------
    # PROCUREMENT
    # -------------------------
    "proc_vendors": (
        "Vendor master containing vendors used for procurement."
    ),

    "proc_purchase_orders": (
        "Purchase order headers containing vendor, amount, dates, "
        "payment terms and PO status."
    ),

    "proc_po_lines": (
        "Individual line items belonging to purchase orders."
    ),

    "proc_po_payment_tranches": (
        "Payment schedule/tranches associated with purchase orders."
    ),

    "proc_po_receipts": (
        "Inventory receiving events associated with purchase order lines."
    ),

    "proc_po_line_regularisations": (
        "Records differences between ordered and actually received quantities."
    ),

    # -------------------------
    # UNEXPECTED RECEIPTS
    # -------------------------
    "proc_unexpected_receipt_headers": (
        "Headers for inventory receiving events that were not initially "
        "associated with a purchase order."
    ),

    "proc_unexpected_receipts": (
        "Line-level details for unexpected/no-PO inventory receipts. "
        "Can optionally be reconciled to a purchase order."
    ),
}


# ============================================================
# IMPLICIT JOINS
# ============================================================

# These relationships exist in the application/data model
# but are NOT enforced with PostgreSQL foreign keys.

IMPLICIT_JOINS = [
    {
        "left": "proc_po_lines.inv_item_id",
        "right": "inv_items.id",
        "description": "PO line references an inventory item.",
    },
    {
        "left": "proc_purchase_orders.delivery_location_id",
        "right": "inv_locations.id",
        "description": "PO delivery location references an inventory location.",
    },
    {
        "left": "proc_po_receipts.location_id",
        "right": "inv_locations.id",
        "description": "PO receipt occurred at an inventory location.",
    },
    {
        "left": "proc_po_receipts.inv_transaction_id",
        "right": "inv_transactions.id",
        "description": (
            "PO receipt links to the inventory transaction that "
            "increments stock."
        ),
    },
    {
        "left": "proc_unexpected_receipts.inv_item_id",
        "right": "inv_items.id",
        "description": "Unexpected receipt references an inventory item.",
    },
    {
        "left": "proc_unexpected_receipts.location_id",
        "right": "inv_locations.id",
        "description": "Unexpected receipt references an inventory location.",
    },
    {
        "left": "proc_unexpected_receipts.inv_transaction_id",
        "right": "inv_transactions.id",
        "description": (
            "Unexpected receipt links to the inventory transaction "
            "that increments stock."
        ),
    },
    {
        "left": "inv_transactions.transfer_location_id",
        "right": "inv_locations.id",
        "description": "Transfer destination location.",
    },
    {
        "left": "inv_transactions.issued_to_id",
        "right": "inv_issued_to_targets.id",
        "description": "Warehouse issue destination.",
    },
]


# ============================================================
# TRANSACTION / POLYMORPHIC RELATIONSHIPS
# ============================================================

TRANSACTION_REFERENCE_RULES = {
    "purchase_order": (
        "reference_id points to proc_po_receipts.id"
    ),
    "unexpected_receipt": (
        "reference_id points to proc_unexpected_receipts.id"
    ),
    "transfer": (
        "reference_id represents the paired transfer relationship "
        "between transfer_out and transfer_in transactions"
    ),
    "warehouse_issue": (
        "issued_to_id identifies the warehouse issue destination"
    ),
}


# ============================================================
# BUSINESS RULES
# ============================================================

BUSINESS_RULES = [
    "proc_purchase_orders.status values are: placed, partial, received.",

    "inv_items.status values are: active, inactive.",

    (
        "inv_transactions.transaction_type values are: "
        "inbound, outbound, transfer_in, transfer_out."
    ),

    (
        "inv_transactions.reference_type values are: "
        "purchase_order, unexpected_receipt, transfer, warehouse_issue."
    ),

    (
        "inbound inventory transactions represent stock entering "
        "a warehouse location."
    ),

    (
        "outbound inventory transactions represent stock leaving "
        "a warehouse location."
    ),

    (
        "transfer_out represents stock leaving the source location."
    ),

    (
        "transfer_in represents stock entering the destination location."
    ),

    (
        "Unexpected receipts represent inventory received without "
        "an associated purchase order at the time of receipt."
    ),

    (
        "PO receiving is represented through proc_po_receipts and "
        "the linked inventory transaction."
    ),

    (
        "Regularisations represent ordered-vs-received quantity variance."
    ),

    (
        "PO status is maintained in proc_purchase_orders.status and "
        "should be used directly for simple PO status questions."
    ),

    (
        "Line-level ordered-vs-received analysis should use "
        "proc_po_lines and receipt/regularisation data."
    ),

    (
        "inv_transactions is the primary source for warehouse movement "
        "history and inventory movement analysis."
    ),

    (
        "inv_field_definitions is excluded from the active agent schema "
        "because it appears unused/legacy."
    ),

    (
        "inv_sub_categories_2.source_id is excluded from join logic "
        "because its purpose is unclear."
    ),
]


# ============================================================
# LIVE DATABASE SCHEMA
# ============================================================

def get_live_schema():
    """
    Read table and column metadata directly from PostgreSQL.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                table_name,
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)

        rows = cursor.fetchall()

        schema = {}

        for table_name, column_name, data_type, nullable in rows:

            if table_name not in schema:
                schema[table_name] = []

            schema[table_name].append({
                "name": column_name,
                "type": data_type,
                "nullable": nullable == "YES",
            })

        return schema

    finally:
        connection.close()


# ============================================================
# BUILD LLM SCHEMA CONTEXT
# ============================================================

def build_schema_context(allowed_tables=None):
    """
    Build database context containing only tables permitted
    for the current persona.

    This is an LLM-context security layer in addition to
    deterministic authorization and SQL validation.
    """

    live_schema = get_live_schema()

    if allowed_tables is not None:
        allowed_tables = {
            table.lower()
            for table in allowed_tables
        }

    context = []

    context.append("DATABASE SCHEMA\n")

    visible_tables = set()

    for table_name, columns in live_schema.items():

        table_key = table_name.lower()

        # Legacy table excluded from active context.
        if table_key == "inv_field_definitions":
            continue

        if (
            allowed_tables is not None
            and table_key not in allowed_tables
        ):
            continue

        visible_tables.add(table_key)

        description = TABLE_DESCRIPTIONS.get(
            table_name,
            "No description available.",
        )

        context.append(
            f"\nTABLE: {table_name}\n"
            f"PURPOSE: {description}\n"
            f"COLUMNS:"
        )

        for column in columns:
            context.append(
                f"  - {column['name']} "
                f"({column['type']}, "
                f"nullable={column['nullable']})"
            )

    # ------------------------------------------------
    # Include only joins whose two tables are visible.
    # ------------------------------------------------

    context.append("\nIMPLICIT JOINS\n")

    for join in IMPLICIT_JOINS:

        left_table = (
            join["left"]
            .split(".", 1)[0]
            .lower()
        )

        right_table = (
            join["right"]
            .split(".", 1)[0]
            .lower()
        )

        if (
            left_table in visible_tables
            and right_table in visible_tables
        ):
            context.append(
                f"- {join['left']} = {join['right']}\n"
                f"  {join['description']}"
            )

    # Inventory transaction reference rules can reveal
    # procurement relationships, so only expose them to
    # personas that can see the referenced domains.
    if "inv_transactions" in visible_tables:

        context.append(
            "\nTRANSACTION REFERENCE RULES\n"
        )

        for key, value in (
            TRANSACTION_REFERENCE_RULES.items()
        ):

            # Warehouse should not be shown procurement
            # table relationships.
            if (
                allowed_tables is not None
                and key
                in {
                    "purchase_order",
                    "unexpected_receipt",
                }
                and not any(
                    table.startswith("proc_")
                    for table in visible_tables
                )
            ):
                continue

            context.append(
                f"- reference_type='{key}': {value}"
            )

    context.append("\nBUSINESS RULES\n")

    for rule in BUSINESS_RULES:

        rule_lower = rule.lower()

        # Avoid exposing procurement-specific business
        # rules to inventory-only personas.
        if (
            allowed_tables is not None
            and not any(
                table.startswith("proc_")
                for table in visible_tables
            )
            and "proc_" in rule_lower
        ):
            continue

        # Avoid exposing inventory-only rules when inventory
        # tables are unavailable.
        if (
            allowed_tables is not None
            and not any(
                table.startswith("inv_")
                for table in visible_tables
            )
            and "inv_" in rule_lower
        ):
            continue

        context.append(f"- {rule}")

    return "\n".join(context)