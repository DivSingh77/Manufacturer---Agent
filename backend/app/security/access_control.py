from app.security.personas import PERSONA_TABLE_ACCESS, VALID_PERSONAS


def validate_persona(persona: str) -> str:
    """
    Validate that the supplied persona is supported.
    """

    persona = persona.lower().strip()

    if persona not in VALID_PERSONAS:
        raise ValueError(
            f"Unknown persona '{persona}'. "
            f"Expected one of: {sorted(VALID_PERSONAS)}"
        )

    return persona


def get_allowed_tables(persona: str) -> set[str]:
    """
    Return tables that this persona is allowed to query.
    """

    persona = validate_persona(persona)

    return PERSONA_TABLE_ACCESS[persona]


def validate_tables_for_persona(
    persona: str,
    tables: list[str],
) -> tuple[bool, list[str]]:
    """
    Check whether all requested tables are accessible
    for a given persona.

    Returns:
        (is_allowed, unauthorized_tables)
    """

    allowed_tables = get_allowed_tables(persona)

    unauthorized = [
        table
        for table in tables
        if table not in allowed_tables
    ]

    return len(unauthorized) == 0, unauthorized