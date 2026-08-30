def query_failure_node(state):

    message = (
        "I couldn't safely answer this question from the "
        "available database schema after multiple attempts. "
        "Please try rephrasing the question."
    )

    return {
        "error": message,
        "answer": message,
        "result_columns": [],
        "result_rows": [],
        "visualization": None,
    }