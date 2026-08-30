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

5. Use the supplied database schema.

6. Use the supplied implicit joins when necessary.

7. Follow the supplied business rules.

8. Do not answer the user's question yourself.
   Return SQL only.

9. Do not use markdown code fences.

10. Return exactly one SQL statement.

11. Prefer explicit column names instead of SELECT *.

12. For simple current-stock questions, use
    inv_current_stock.

13. For inventory movement/history questions,
    use inv_transactions.

14. For purchase-order questions,
    use proc_purchase_orders and related procurement tables.

15. Do not access procurement tables for the warehouse persona.

16. The database uses PostgreSQL syntax.

17. For purchase-order receipt questions, ALWAYS follow this join path:

    proc_purchase_orders.id
        -> proc_po_lines.po_id
        -> proc_po_receipts.po_line_id

    Correct pattern:
    proc_purchase_orders po
    JOIN proc_po_lines pol ON pol.po_id = po.id
    JOIN proc_po_receipts r ON r.po_line_id = pol.id

    When human-readable receipt details are requested, also join:
    proc_po_lines.inv_item_id -> inv_items.id
    proc_po_receipts.location_id -> inv_locations.id

    Do NOT join proc_po_receipts directly to proc_purchase_orders.
    Do NOT use an IN subquery to connect receipts to purchase orders when the direct po_lines relationship can be used.
"""


def generate_sql(question: str, persona: str) -> str:

    allowed_tables = get_allowed_tables(persona)

    schema_context = build_schema_context()

    user_prompt = f"""
USER PERSONA:
{persona}

ALLOWED TABLES:
{sorted(allowed_tables)}

DATABASE CONTEXT:
{schema_context}

USER QUESTION:
{question}

Generate exactly one PostgreSQL SELECT statement.
Return SQL only.
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

    sql = response.choices[0].message.content.strip()

    # Defensive cleanup in case the model returns markdown.
    if sql.startswith("```"):
        sql = sql.replace("```sql", "")
        sql = sql.replace("```", "")
        sql = sql.strip()

    return sql