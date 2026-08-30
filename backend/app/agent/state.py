from typing import Any, TypedDict


class AgentState(TypedDict, total=False):

    # Original request
    question: str

    # User role
    persona: str

    # What the classifier determines
    intent: str
    domain: str

    # Security
    allowed_tables: list[str]

    # Database intelligence
    schema_context: str

    # Generated SQL
    sql: str

    # Validation
    sql_valid: bool
    validation_error: str
    
    execution_error: str | None

    # Database result
    result_columns: list[str]
    result_rows: list[Any]

    # Final answer
    answer: str

    # Visualization
    visualization: dict | None

    # Error handling
    error: str | None

    # Retry tracking
    retry_count: int