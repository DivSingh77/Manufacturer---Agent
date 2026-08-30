from app.security.access_control import get_allowed_tables, validate_persona

PERSONA_ALLOWED_DOMAINS = {
    "warehouse": {
        "inventory",
    },
    "procurement": {
        "procurement",
    },
    "owner": {
        "inventory",
        "procurement",
        "cross_domain",
    },
}


def access_guard_node(state):

    persona = state.get("persona", "")
    domain = state.get("domain", "")

    try:
        persona = validate_persona(persona)

        allowed_domains = PERSONA_ALLOWED_DOMAINS[persona]

        if domain not in allowed_domains:
            return {
                "persona": persona,
                "allowed_tables": [],
                "error": (
                    f"Access denied: {persona} users cannot "
                    f"access this business domain."
                ),
            }

        allowed_tables = sorted(
            get_allowed_tables(persona)
        )

        return {
            "persona": persona,
            "allowed_tables": allowed_tables,
            "error": None,
        }

    except ValueError:
        return {
            "allowed_tables": [],
            "error": "Access denied: invalid persona.",
        }