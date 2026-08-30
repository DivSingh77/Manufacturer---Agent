from app.security.access_control import get_allowed_tables, validate_persona


def access_guard_node(state):

    persona = state.get("persona", "")
    domain = state.get("domain", "")

    try:
        persona = validate_persona(persona)

        # Warehouse has inventory-only access
        if persona == "warehouse" and domain == "procurement":
            raise ValueError(
                "Access denied: warehouse users cannot access procurement data."
            )

        # Procurement may use inv_items / inv_locations only as lookup
        # tables while answering PROCUREMENT questions.
        #
        # A direct inventory-analysis question such as current stock
        # must therefore be denied.
        if persona == "procurement" and domain == "inventory":
            raise ValueError(
                "Access denied: procurement users cannot perform inventory analysis."
            )

        allowed_tables = list(get_allowed_tables(persona))

        return {
            "persona": persona,
            "allowed_tables": allowed_tables,
            "error": None,
        }

    except ValueError as e:
        return {
            "error": str(e),
        }