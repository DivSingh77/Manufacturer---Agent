from app.sql.executor import execute_query


def execute_sql_node(state):

    result = execute_query(
        state["sql"]
    )

    return {
        "result_columns": result["columns"],
        "result_rows": result["rows"],
    }