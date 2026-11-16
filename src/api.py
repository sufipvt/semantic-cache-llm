from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

from src.main import ask_question
from src.cache import get_cache_stats, check_redis_connection


app = FastAPI(
    title="Redis Semantic Cache API",
    description="Semantic caching for LLM applications using Redis Vector Search and Groq.",
    version="1.0.0"
)


class AskRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description="Question to send to the LLM."
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        if not value.strip():
            raise ValueError("Question cannot be empty or whitespace.")
        return value


@app.post("/ask", summary="Ask a question")
def ask(request: AskRequest):

    answer = ask_question(request.question)

    return {
        "question": request.question,
        "answer": answer
    }


@app.get("/stats", summary="Get cache statistics")
def stats():

    return get_cache_stats()


@app.get("/health", summary="Check API and Redis health")
def health():

    redis_status = check_redis_connection()

    return {
        "api": "healthy",
        "redis": "connected" if redis_status else "disconnected",
        "cache": "available" if redis_status else "degraded",
        "status": "healthy" if redis_status else "degraded"
    }