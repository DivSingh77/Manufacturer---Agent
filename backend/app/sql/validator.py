from app.security.access_control import get_allowed_tables
from sqlglot import exp, parse
from sqlglot.errors import ParseError

FORBIDDEN_NODE_TYPES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Create,
    exp.Alter,
    exp.Command,
    exp.Merge,
)


def extract_tables(sql: str) -> set[str]:
    """
    Parse SQL into an AST and return every physical table referenced.

    This catches:
    - FROM table
    - JOIN table
    - comma joins
    - nested subqueries
    - CTE bodies
    """

    try:
        statements = parse(sql, read="postgres")
    except ParseError as exc:
        raise ValueError(f"SQL parsing failed: {exc}") from exc

    if len(statements) != 1:
        raise ValueError("Only one SQL statement is allowed.")

    statement = statements[0]

    # CTE names are aliases, not real database tables.
    cte_names = {
        cte.alias_or_name.lower()
        for cte in statement.find_all(exp.CTE)
        if cte.alias_or_name
    }

    tables = set()

    for table in statement.find_all(exp.Table):
        table_name = table.name

        if not table_name:
            continue

        table_name = table_name.lower()

        if table_name not in cte_names:
            tables.add(table_name)

    return tables


def validate_sql(
    sql: str,
    persona: str,
) -> tuple[bool, str]:

    cleaned = (sql or "").strip()

    if not cleaned:
        return False, "SQL is empty."

    try:
        statements = parse(cleaned, read="postgres")
    except ParseError:
        return False, "Generated SQL could not be safely parsed."

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed."

    statement = statements[0]

    # --------------------------------------------------
    # Read-only enforcement
    # --------------------------------------------------

    if not isinstance(
        statement,
        (exp.Select, exp.Union, exp.Intersect, exp.Except),
    ):
        # WITH queries generally parse to the underlying SELECT,
        # so legitimate CTE SELECTs remain allowed.
        return False, "Only read-only SELECT queries are allowed."

    # Defense against writes hidden inside more complex syntax.
    for forbidden_type in FORBIDDEN_NODE_TYPES:
        if statement.find(forbidden_type):
            return False, "Only read-only SELECT queries are allowed."

    # --------------------------------------------------
    # Persona table allowlist
    # --------------------------------------------------

    try:
        referenced_tables = extract_tables(cleaned)
    except ValueError as exc:
        return False, str(exc)

    if not referenced_tables:
        return False, "Query does not reference a permitted database table."

    allowed_tables = {
        table.lower()
        for table in get_allowed_tables(persona)
    }

    unauthorized = referenced_tables - allowed_tables

    if unauthorized:
        return (
            False,
            "Query references tables not permitted for this persona.",
        )

    return True, "SQL is valid."