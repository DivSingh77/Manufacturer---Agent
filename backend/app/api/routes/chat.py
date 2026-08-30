from app.agent.graph import agent_graph
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    persona: str


@router.post("/chat")
def chat(request: ChatRequest):

    try:

        result = agent_graph.invoke(
            {
                "question": request.question,
                "persona": request.persona,
            }
        )

        return {
            "answer": result.get("answer"),
            "persona": result.get("persona"),
            "domain": result.get("domain"),
            "intent": result.get("intent"),
            "sql": result.get("sql"),

            "data": {
                "columns": result.get("result_columns", []),
                "rows": result.get("result_rows", []),
            },

            "visualization": result.get("visualization"),
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )