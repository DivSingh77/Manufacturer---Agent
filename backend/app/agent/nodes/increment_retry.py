def increment_retry_node(state):

    current = state.get(
        "retry_count",
        0,
    )

    return {
        "retry_count": current + 1,
    }