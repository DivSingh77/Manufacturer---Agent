from app.sql.generator import generate_sql


def generate_sql_node(state):

    retry_count = state.get(
        "retry_count",
        0,
    )

    sql = generate_sql(
        question=state["question"],
        persona=state["persona"],
        validation_error=state.get(
            "validation_error"
        ),
        execution_error=state.get(
            "execution_error"
        ),
        previous_sql=state.get("sql"),
    )

    return {
        "sql": sql,
        "sql_valid": None,
        "validation_error": None,
        "execution_error": None,
        "retry_count": retry_count,
    }