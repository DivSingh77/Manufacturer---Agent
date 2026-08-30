from app.response.visualization import build_visualization


def visualization_node(state):
    """
    Build chart metadata from the query result when
    visualization is useful for the current intent.
    """

    intent = state.get("intent")

    columns = state.get(
        "result_columns",
        [],
    )

    rows = state.get(
        "result_rows",
        [],
    )

    visualization = build_visualization(
        intent=intent,
        columns=columns,
        rows=rows,
    )

    return {
        "visualization": visualization,
    }