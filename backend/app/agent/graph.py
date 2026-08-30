from app.agent.nodes.access_guard import access_guard_node
from app.agent.nodes.classify import classify_question
from app.agent.nodes.execute_sql import execute_sql_node
from app.agent.nodes.generate_sql import generate_sql_node
from app.agent.nodes.respond import respond_node
from app.agent.nodes.validate_sql import validate_sql_node
from app.agent.nodes.visualize import visualization_node
from app.agent.state import AgentState
from langgraph.graph import END, StateGraph


def access_router(state):
    """
    Route based on persona/domain authorization.
    """

    if state.get("error"):
        return "denied"

    return "allowed"


def validation_router(state):
    """
    Route based on SQL validation.
    """

    if state.get("sql_valid"):
        return "execute"

    if state.get("retry_count", 0) < 1:
        return "regenerate"

    return "end"


def regenerate_sql(state):
    """
    Increment retry counter before regenerating SQL.
    """

    return {
        "retry_count": state.get("retry_count", 0) + 1
    }


def build_graph():

    graph = StateGraph(AgentState)

    # -------------------------
    # Nodes
    # -------------------------

    graph.add_node(
        "classify",
        classify_question,
    )

    graph.add_node(
        "access_guard",
        access_guard_node,
    )

    graph.add_node(
        "generate_sql",
        generate_sql_node,
    )

    graph.add_node(
        "validate_sql",
        validate_sql_node,
    )

    graph.add_node(
        "execute_sql",
        execute_sql_node,
    )

    graph.add_node(
        "respond",
        respond_node,
    )

    graph.add_node(
        "regenerate",
        regenerate_sql,
    )
    
    graph.add_node(
        "visualize",
        visualization_node,
    )

    # -------------------------
    # Entry
    # -------------------------

    graph.set_entry_point("classify")

    # -------------------------
    # Classification
    # -------------------------

    graph.add_edge(
        "classify",
        "access_guard",
    )

    # -------------------------
    # Access control
    # -------------------------

    graph.add_conditional_edges(
        "access_guard",
        access_router,
        {
            "allowed": "generate_sql",
            "denied": "respond",
        },
    )

    # -------------------------
    # SQL generation
    # -------------------------

    graph.add_edge(
        "generate_sql",
        "validate_sql",
    )

    # -------------------------
    # SQL validation
    # -------------------------

    graph.add_conditional_edges(
        "validate_sql",
        validation_router,
        {
            "execute": "execute_sql",
            "regenerate": "regenerate",
            "end": END,
        },
    )

    graph.add_edge(
        "regenerate",
        "generate_sql",
    )

    # -------------------------
    # Execution
    # -------------------------

    graph.add_edge(
        "execute_sql",
        "visualize",
    )

    graph.add_edge(
        "visualize",
        "respond",
    )

    # -------------------------
    # Final response
    # -------------------------

    graph.add_edge(
        "respond",
        END,
    )

    return graph.compile()


agent_graph = build_graph()