from app.database.connection import get_connection


def execute_query(sql: str):

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(sql)

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        return {
            "columns": columns,
            "rows": rows,
        }

    finally:
        connection.close()