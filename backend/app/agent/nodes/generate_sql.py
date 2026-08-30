from app.security.access_control import get_allowed_tables
from app.sql.generator import generate_sql


def generate_sql_node(state):

    question = state["question"]
    persona = state["persona"]

    sql = generate_sql(
        question,
        persona,
    )

    return {
        "sql": sql,
    }