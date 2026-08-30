from app.sql.validator import validate_sql


def validate_sql_node(state):

    sql = state["sql"]
    persona = state["persona"]

    valid, message = validate_sql(
        sql,
        persona,
    )

    return {
        "sql_valid": valid,
        "validation_error": None if valid else message,
    }