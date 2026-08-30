from app.sql.executor import execute_query
from app.sql.generator import generate_sql
from app.sql.validator import validate_sql


def test_question(question: str, persona: str):

    print("\n" + "=" * 80)
    print("QUESTION")
    print("=" * 80)

    print(question)

    print("\nPERSONA:")
    print(persona)

    # ---------------------------------------------------------
    # GENERATE
    # ---------------------------------------------------------

    sql = generate_sql(
        question,
        persona,
    )

    print("\n" + "=" * 80)
    print("GENERATED SQL")
    print("=" * 80)

    print(sql)

    # ---------------------------------------------------------
    # VALIDATE
    # ---------------------------------------------------------

    valid, message = validate_sql(
        sql,
        persona,
    )

    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)

    print(valid)
    print(message)

    if not valid:
        return

    # ---------------------------------------------------------
    # EXECUTE
    # ---------------------------------------------------------

    result = execute_query(sql)

    print("\n" + "=" * 80)
    print("RESULT")
    print("=" * 80)

    print("Columns:")
    print(result["columns"])

    print("\nRows:")

    for row in result["rows"][:20]:
        print(row)


if __name__ == "__main__":

    test_question(
        "What is the current stock of all items?",
        "warehouse",
    )