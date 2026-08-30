import os

from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

LANGCHAIN_TRACING_V2 = os.getenv(
    "LANGCHAIN_TRACING_V2",
    "false"
)

LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

LANGCHAIN_PROJECT = os.getenv(
    "LANGCHAIN_PROJECT",
    "manufacturer-agent"
)


if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")