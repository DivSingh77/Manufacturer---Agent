from app.database.connection import get_connection

MAX_RESULT_ROWS = 500
STATEMENT_TIMEOUT_MS = 10_000


def execute_query(sql: str):

    connection = get_connection()

    try:
        # Prevent accidental persistence even if something
        # unexpected gets through application validation.
        connection.set_session(
            readonly=True,
            autocommit=False,
        )

        cursor = connection.cursor()

        # Prevent expensive/hanging generated queries.
        cursor.execute(
            f"SET LOCAL statement_timeout = "
            f"{STATEMENT_TIMEOUT_MS};"
        )

        cursor.execute(sql)

        columns = [
            description[0]
            for description in cursor.description
        ]

        # Bound memory/API payload size.
        rows = cursor.fetchmany(MAX_RESULT_ROWS)

        connection.rollback()

        return {
            "columns": columns,
            "rows": rows,
        }

    finally:
        connection.close()