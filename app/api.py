
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.graph.neo4j_connection import Neo4jConnection
from src.graphrag.graph_retrieval import run_graphrag


# Shared Neo4j connection
connection = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global connection

    connection = Neo4jConnection()
    connection.verify_connection()

    yield

    if connection:
        connection.close()


app = FastAPI(
    title="VentureLens GraphRAG API",
    description="AI-powered Tech Startup Knowledge Graph and GraphRAG API",
    version="1.0.0",
    lifespan=lifespan
)


class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="User question about technology startups"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10
    )


class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]


@app.get("/")
def home():
    return {
        "message": "Welcome to VentureLens GraphRAG API",
        "status": "running"
    }


@app.get("/health")
def health():
    if connection is None:
        raise HTTPException(
            status_code=503,
            detail="Neo4j connection is not available"
        )

    return {
        "status": "healthy",
        "database": "connected"
    }


@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    if connection is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection is not available"
        )

    try:
        result = run_graphrag(
            connection=connection,
            question=request.question,
            top_k=request.top_k
        )

        return QuestionResponse(
            question=request.question,
            answer=result["answer"],
            sources=result["sources"]
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"GraphRAG processing failed: {str(error)}"
        )
