from app.response.visualization import build_visualization


def visualization_node(state):

    visualization = build_visualization(state)

    return {
        "visualization": visualization
    }