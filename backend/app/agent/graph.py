from app.agent.nodes.access_guard import access_guard_node
from app.agent.nodes.classify import classify_question
from app.agent.nodes.execute_sql import execute_sql_node
from app.agent.nodes.generate_sql import generate_sql_node
from app.agent.nodes.increment_retry import increment_retry_node
from app.agent.nodes.query_failure import query_failure_node
from app.agent.nodes.respond import respond_node
from app.agent.nodes.validate_sql import validate_sql_node
from app.agent.nodes.visualize import visualization_node
from app.agent.state import AgentState
from langgraph.graph import END, StateGraph

# ============================================================
# Retry configuration
# ============================================================

# Two repair attempts are allowed after the initial SQL attempt.
#
# Attempt 1
#   -> failure
# Retry 1
#   -> failure
# Retry 2
#   -> failure
# Safe failure response
#
MAX_SQL_RETRIES = 2


# ============================================================
# Router: Access Control
# ============================================================

def access_router(state: AgentState) -> str:
    """
    Decide whether the request should continue to SQL generation.

    access_guard_node places a safe message in state["error"]
    whenever the persona is not allowed to access the requested
    business domain.
    """

    if state.get("error"):
        return "denied"

    return "allowed"


# ============================================================
# Router: SQL Validation
# ============================================================

def validation_router(state: AgentState) -> str:
    """
    Decide what to do after deterministic SQL validation.

    valid:
        Execute the SQL.

    retry:
        Increment retry counter and ask the LLM to repair SQL.

    failed:
        Retry limit reached. Return a safe user-facing response.

    IMPORTANT:
    We intentionally do NOT route exhausted retries directly to END.
    Otherwise the graph could terminate without populating "answer".
    """

    if state.get("sql_valid") is True:
        return "valid"

    retry_count = state.get("retry_count", 0)

    if retry_count < MAX_SQL_RETRIES:
        return "retry"

    return "failed"


# ============================================================
# Router: SQL Execution
# ============================================================

def execution_router(state: AgentState) -> str:
    """
    Decide what to do after PostgreSQL execution.

    success:
        Continue to visualization and response generation.

    retry:
        SQL was syntactically/security-valid but failed at runtime.
        Give the SQL generator another opportunity to repair it.

    failed:
        Runtime execution continued failing after the retry limit.
        Return a safe failure response instead of leaking DB errors.
    """

    execution_error = state.get("execution_error")

    if not execution_error:
        return "success"

    retry_count = state.get("retry_count", 0)

    if retry_count < MAX_SQL_RETRIES:
        return "retry"

    return "failed"


# ============================================================
# Build LangGraph
# ============================================================

workflow = StateGraph(AgentState)


# ============================================================
# Register Nodes
# ============================================================

workflow.add_node(
    "classify",
    classify_question,
)

workflow.add_node(
    "access_guard",
    access_guard_node,
)

workflow.add_node(
    "generate_sql",
    generate_sql_node,
)

workflow.add_node(
    "validate_sql",
    validate_sql_node,
)

workflow.add_node(
    "execute_sql",
    execute_sql_node,
)

workflow.add_node(
    "increment_retry",
    increment_retry_node,
)

workflow.add_node(
    "query_failure",
    query_failure_node,
)

workflow.add_node(
    "visualize",
    visualization_node,
)

workflow.add_node(
    "respond",
    respond_node,
)


# ============================================================
# Entry Point
# ============================================================

workflow.set_entry_point(
    "classify"
)


# ============================================================
# Classification -> Access Guard
# ============================================================

workflow.add_edge(
    "classify",
    "access_guard",
)


# ============================================================
# Access Control Routing
# ============================================================

workflow.add_conditional_edges(
    "access_guard",
    access_router,
    {
        "allowed": "generate_sql",
        "denied": "respond",
    },
)


# ============================================================
# SQL Generation -> Validation
# ============================================================

workflow.add_edge(
    "generate_sql",
    "validate_sql",
)


# ============================================================
# SQL Validation Routing
# ============================================================

workflow.add_conditional_edges(
    "validate_sql",
    validation_router,
    {
        # SQL passed deterministic validation.
        "valid": "execute_sql",

        # SQL failed validation but retry budget remains.
        "retry": "increment_retry",

        # SQL repeatedly failed validation.
        "failed": "query_failure",
    },
)


# ============================================================
# Retry -> SQL Generation
# ============================================================

workflow.add_edge(
    "increment_retry",
    "generate_sql",
)


# ============================================================
# SQL Execution Routing
# ============================================================

workflow.add_conditional_edges(
    "execute_sql",
    execution_router,
    {
        # Database execution succeeded.
        "success": "visualize",

        # Query passed validation but PostgreSQL rejected it.
        # Retry with the actual execution error available internally.
        "retry": "increment_retry",

        # Runtime failures continued after maximum retries.
        "failed": "query_failure",
    },
)


# ============================================================
# Successful Execution -> Visualization -> Response
# ============================================================

workflow.add_edge(
    "visualize",
    "respond",
)


# ============================================================
# Response -> End
# ============================================================

workflow.add_edge(
    "respond",
    END,
)


# ============================================================
# Safe Query Failure -> End
# ============================================================

workflow.add_edge(
    "query_failure",
    END,
)


# ============================================================
# Compile Graph
# ============================================================

agent_graph = workflow.compile()