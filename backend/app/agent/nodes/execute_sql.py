from app.sql.executor import execute_query


def execute_sql_node(state):

    sql = state.get("sql")

    if not sql:
        return {
            "execution_error": (
                "No SQL was available for execution."
            ),
            "result_columns": [],
            "result_rows": [],
        }

    try:

        result = execute_query(sql)

        return {
            "result_columns": result["columns"],
            "result_rows": result["rows"],
            "execution_error": None,
        }

    except Exception as exc:

        # Keep the database error internal.
        # Do not expose this directly to the frontend.
        return {
            "result_columns": [],
            "result_rows": [],
            "execution_error": str(exc),
        }