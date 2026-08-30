PERSONA_TABLE_ACCESS = {

    "warehouse": {
        "inv_items",
        "inv_categories",
        "inv_sub_categories",
        "inv_sub_categories_2",
        "inv_locations",
        "inv_current_stock",
        "inv_issued_to_targets",
        "inv_transactions",
    },

    "procurement": {
        "proc_vendors",
        "proc_purchase_orders",
        "proc_po_lines",
        "proc_po_payment_tranches",
        "proc_po_receipts",
        "proc_po_line_regularisations",
        "proc_unexpected_receipt_headers",
        "proc_unexpected_receipts",

        # Lookup-only in the business design.
        # For MVP we allow table-level access.
        "inv_items",
        "inv_locations",
    },

    "owner": {
        "inv_items",
        "inv_categories",
        "inv_sub_categories",
        "inv_sub_categories_2",
        "inv_locations",
        "inv_current_stock",
        "inv_issued_to_targets",
        "inv_transactions",
        "inv_field_definitions",

        "proc_vendors",
        "proc_purchase_orders",
        "proc_po_lines",
        "proc_po_payment_tranches",
        "proc_po_receipts",
        "proc_po_line_regularisations",
        "proc_unexpected_receipt_headers",
        "proc_unexpected_receipts",
    },
}


VALID_PERSONAS = set(PERSONA_TABLE_ACCESS.keys())