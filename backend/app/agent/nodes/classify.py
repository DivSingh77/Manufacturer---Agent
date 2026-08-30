from app.config import OPENAI_API_KEY
from app.security.access_control import validate_persona
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)


CLASSIFIER_PROMPT = """
You classify questions for a manufacturing inventory
and procurement assistant.

Possible domains:

- inventory
- procurement
- cross_domain

Possible intents include:

- current_stock
- stock_by_location
- inventory_history
- inventory_movement
- purchase_order_status
- purchase_order_details
- vendor_analysis
- purchase_history
- price_history
- receipt_analysis
- regularisation_analysis
- unexpected_receipts
- general

Return exactly this format:

DOMAIN: <domain>
INTENT: <intent>

Do not provide any explanation.
"""


def classify_question(state):

    question = state["question"]
    persona = validate_persona(state["persona"])

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": CLASSIFIER_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    output = response.choices[0].message.content.strip()

    domain = "general"
    intent = "general"

    for line in output.splitlines():

        if line.startswith("DOMAIN:"):
            domain = line.split(":", 1)[1].strip()

        elif line.startswith("INTENT:"):
            intent = line.split(":", 1)[1].strip()

    return {
        "persona": persona,
        "domain": domain,
        "intent": intent,
        "retry_count": 0,
    }