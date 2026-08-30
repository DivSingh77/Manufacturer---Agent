from app.config import OPENAI_API_KEY
from app.database.schema import build_schema_context
from app.security.access_control import get_allowed_tables
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are an expert PostgreSQL SQL generation assistant
for a manufacturing inventory and procurement system.

Your job is to convert a user's natural-language question
into ONE safe, read-only PostgreSQL SELECT query.

IMPORTANT RULES:

1. Generate SELECT queries only.

2. Never generate:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   TRUNCATE
   CREATE
   GRANT
   REVOKE

3. Only use tables explicitly allowed for the user's persona.

4. Do not invent tables or columns.

5. Use only the supplied database schema.

6. Use the supplied implicit joins when necessary.

7. Follow the supplied business rules.

8. Do not answer the user's question yourself.
   Return SQL only.

9. Do not use markdown code fences.

10. Return exactly one SQL statement.

11. Prefer explicit column names instead of SELECT *.

12. For simple current-stock questions, use:
    inv_current_stock

13. For inventory movement/history questions, use:
    inv_transactions

14. For purchase-order questions, use:
    proc_purchase_orders
    and related procurement tables.

15. Do not access procurement tables for the warehouse persona.

16. The database uses PostgreSQL syntax.

17. For purchase-order receipt questions, ALWAYS follow
    this relationship:

    proc_purchase_orders.id
        ->
    proc_po_lines.po_id

    proc_po_lines.id
        ->
    proc_po_receipts.po_line_id

    Correct join pattern:

    proc_purchase_orders po
    JOIN proc_po_lines pol
        ON pol.po_id = po.id
    JOIN proc_po_receipts r
        ON r.po_line_id = pol.id

18. When human-readable receipt details are requested,
    also use:

    proc_po_lines.inv_item_id
        ->
    inv_items.id

    proc_po_receipts.location_id
        ->
    inv_locations.id

19. Do NOT join proc_po_receipts directly to
    proc_purchase_orders.

20. Do NOT use an IN subquery to connect receipts
    to purchase orders when the direct po_lines
    relationship can be used.

21. For human-readable inventory transaction questions,
    prefer joining:

    inv_transactions.item_id
        ->
    inv_items.id

    inv_transactions.location_id
        ->
    inv_locations.id

    instead of returning only UUIDs.

22. For human-readable purchase-order questions,
    use:

    proc_purchase_orders.vendor_id
        ->
    proc_vendors.id

    proc_po_lines.inv_item_id
        ->
    inv_items.id

    when vendor or item information is requested.

23. For zero-stock questions, include items that may not
    have any inv_current_stock rows by using an appropriate
    LEFT JOIN and COALESCE when necessary.

24. For stock totals across locations, aggregate quantities
    using SUM where appropriate.

25. Never assume a status value that is not present in the
    supplied schema/business rules.

26. If a previous SQL attempt failed, carefully inspect the
    provided validation or database execution error and fix
    the query.

27. When repairing a failed query:
    - Do not repeat the same SQL unchanged.
    - Do not invent a replacement column.
    - Re-check the supplied schema.
    - Preserve persona restrictions.
    - Preserve read-only behavior.
"""


def generate_sql(
    question: str,
    persona: str,
    validation_error: str | None = None,
    execution_error: str | None = None,
    previous_sql: str | None = None,
) -> str:
    """
    Generate one safe PostgreSQL SELECT statement.

    On retry, the previous SQL and its failure information
    are provided to the model so it can repair the query.

    Security note:
    build_schema_context() receives only the tables allowed
    for the current persona. Therefore the model does not
    receive the complete database schema for restricted
    personas.
    """

    allowed_tables = get_allowed_tables(persona)

    # Important security improvement:
    # only expose schema belonging to tables this persona
    # is permitted to access.
    schema_context = build_schema_context(
        allowed_tables=allowed_tables
    )

    retry_context = ""

    if previous_sql and (
        validation_error or execution_error
    ):
        retry_context = f"""
PREVIOUS SQL ATTEMPT:
{previous_sql}

THE PREVIOUS QUERY FAILED AND MUST BE CORRECTED.

VALIDATION ERROR:
{validation_error or "None"}

DATABASE EXECUTION ERROR:
{execution_error or "None"}

REPAIR INSTRUCTIONS:
- Determine why the previous SQL failed.
- Re-check the supplied schema carefully.
- Correct the SQL.
- Do not repeat the same mistake.
- Do not invent tables or columns.
- Continue using only the allowed tables.
- Return exactly one read-only PostgreSQL SELECT statement.
"""

    user_prompt = f"""
USER PERSONA:
{persona}

ALLOWED TABLES:
{sorted(allowed_tables)}

DATABASE CONTEXT:
{schema_context}

USER QUESTION:
{question}

{retry_context}

Generate exactly one PostgreSQL SELECT statement.

Requirements:
- Use only tables listed under ALLOWED TABLES.
- Use only columns shown in DATABASE CONTEXT.
- Follow the supplied relationships and business rules.
- Never modify the database.
- Never invent data.
- Return SQL only.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    sql = (
        response.choices[0]
        .message.content
        .strip()
    )

    # Defensive cleanup in case the model still returns
    # markdown despite being instructed not to.
    if sql.startswith("```"):
        sql = sql.replace("```sql", "")
        sql = sql.replace("```SQL", "")
        sql = sql.replace("```", "")
        sql = sql.strip()

    return sql