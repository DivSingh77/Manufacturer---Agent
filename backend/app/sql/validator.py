import re

import sqlparse
from app.security.access_control import get_allowed_tables

FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
}


def extract_tables(sql: str) -> set[str]:

    tables = set()

    parsed = sqlparse.parse(sql)

    if not parsed:
        return tables

    statement = parsed[0]

    tokens = list(statement.flatten())

    for i, token in enumerate(tokens):

        if token.ttype and token.ttype in sqlparse.tokens.Keyword:

            if token.value.upper() in {"FROM", "JOIN"}:

                # Find the next meaningful token
                for next_token in tokens[i + 1:]:

                    if next_token.is_whitespace:
                        continue

                    value = next_token.value.strip()

                    value = value.strip('"')

                    # Remove aliases
                    value = value.split()[0]

                    # Handle schema-qualified names
                    value = value.split(".")[-1]

                    if re.match(
                        r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                        value,
                    ):
                        tables.add(value.lower())

                    break

    return tables


def validate_sql(
    sql: str,
    persona: str,
) -> tuple[bool, str]:

    cleaned = sql.strip()

    if not cleaned:
        return False, "SQL is empty."

    # Only one statement.
    statements = sqlparse.parse(cleaned)

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed."

    # Must begin with SELECT or WITH.
    first_word = cleaned.split()[0].upper()

    if first_word not in {"SELECT", "WITH"}:
        return False, "Only SELECT queries are allowed."

    # Forbidden operations.
    upper_sql = cleaned.upper()

    for keyword in FORBIDDEN_KEYWORDS:

        if re.search(
            rf"\b{keyword}\b",
            upper_sql,
        ):
            return False, f"Forbidden SQL operation: {keyword}"

    # Persona access validation.
    referenced_tables = extract_tables(cleaned)

    allowed_tables = {
        table.lower()
        for table in get_allowed_tables(persona)
    }

    unauthorized = referenced_tables - allowed_tables

    if unauthorized:
        return (
            False,
            "Unauthorized tables: "
            + ", ".join(sorted(unauthorized))
        )

    return True, "SQL is valid."