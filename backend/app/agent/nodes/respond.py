from app.config import OPENAI_API_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)


def respond_node(state):
    
    if state.get("error"):
        return {
            "answer": state["error"]
        }

    question = state["question"]
    rows = state.get("result_rows", [])
    columns = state.get("result_columns", [])

    result_text = "\n".join(
        str(dict(zip(columns, row)))
        for row in rows[:100]
    )

    prompt = f"""
You are a helpful manufacturing inventory and procurement assistant.

Answer the user's question using ONLY the database results below.

Do not invent information.

If there are no results, clearly say that no matching records
were found.

Be concise but useful.

USER QUESTION:
{question}

DATABASE RESULTS:

{result_text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You summarize database query results accurately. "
                    "Never fabricate facts."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return {
        "answer": response.choices[0].message.content.strip()
    }