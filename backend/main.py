"""
FastAPI backend for Verra carbon credit chatbot.
Provides API endpoints for querying the VCU database via Vanna AI.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from init_db import load_and_clean_csv, init_database, DB_PATH, CSV_PATH
from vanna_setup import setup_vanna, get_vanna, execute_query
from metrics import (
    get_metrics_summary,
    get_hot_projects,
    get_emerging_projects,
    get_slowing_projects,
)
from training_data import CHATBOT_QUESTIONS

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Verra VCU Chatbot API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Vanna instance
vn = None


# Pydantic models
class ChatMessage(BaseModel):
    message: str
    history: Optional[list] = []


class ChatResponse(BaseModel):
    text: str
    sql: Optional[str] = None
    data: Optional[list] = None
    chart_spec: Optional[dict] = None
    error: Optional[str] = None


class DataSummary(BaseModel):
    total_projects: int
    total_countries: int
    total_credits_issued: float
    total_credits_retired: float
    quadrant_distribution: dict
    velocity_stats: dict
    momentum_stats: dict


class SuggestedQuestions(BaseModel):
    categories: dict


@app.on_event("startup")
async def startup_event():
    """Initialize database and Vanna on startup."""
    global vn

    print("Startup: Checking database...")

    # Initialize database if not exists
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Initializing...")
        df = load_and_clean_csv()
        init_database(df)

    # Initialize Vanna
    print("Setting up Vanna AI...")
    vn = get_vanna()
    print("Vanna ready!")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """
    Main chat endpoint.
    Takes a natural language question and returns SQL, data, and optional chart.
    """
    if not vn:
        raise HTTPException(status_code=500, detail="Vanna not initialized")

    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        # Execute query through Vanna
        result = execute_query(vn, request.message)

        if result["success"]:
            return ChatResponse(
                text=result["text"],
                sql=result["sql"],
                data=result["data"],
                chart_spec=result["chart_spec"],
                error=None,
            )
        else:
            return ChatResponse(
                text="Sorry, I couldn't process that query.",
                sql=None,
                data=None,
                chart_spec=None,
                error=result["error"],
            )

    except Exception as e:
        print(f"Chat error: {e}")
        return ChatResponse(
            text="An error occurred while processing your query.",
            sql=None,
            data=None,
            chart_spec=None,
            error=str(e),
        )


@app.get("/api/data/summary", response_model=DataSummary)
async def data_summary():
    """
    Get overall dataset summary including metrics distribution.
    """
    try:
        summary = get_metrics_summary()

        return DataSummary(
            total_projects=summary["total_projects"],
            total_countries=summary["total_countries"],
            total_credits_issued=summary["total_credits_issued"],
            total_credits_retired=summary["total_credits_retired"],
            quadrant_distribution=summary["quadrant_distribution"],
            velocity_stats=summary["velocity"],
            momentum_stats=summary["momentum"],
        )

    except Exception as e:
        print(f"Summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/suggestions", response_model=SuggestedQuestions)
async def suggested_questions():
    """
    Get curated suggested questions for the user.
    Organized by category.
    """
    suggestions = {
        "Momentum": [
            "Which projects are heating up?",
            "Which projects are slowing down?",
            "Where are emerging opportunities in energy projects?",
        ],
        "Supply": [
            "Show hot projects to warehouse",
            "Which projects have high velocity?",
            "Show projects with rising momentum",
        ],
        "Market Intelligence": [
            "Who are the top intermediaries?",
            "Compare market activity by country",
            "How many projects have CORSIA certification?",
        ],
        "Analytics": [
            "Compare average momentum by country",
            "Average velocity by project type",
            "Show SDG distribution",
        ],
        "Project Deep Dive": [
            "Show all retirement events for recent projects",
            "What is the retirement pattern by beneficiary?",
            "Which projects have the most unique beneficiaries?",
        ],
    }

    return SuggestedQuestions(categories=suggestions)


@app.get("/api/data/hot-projects")
async def hot_projects(limit: int = 10):
    """Get top hot projects."""
    try:
        projects = get_hot_projects(limit)
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/emerging-projects")
async def emerging_projects(limit: int = 10):
    """Get emerging projects."""
    try:
        projects = get_emerging_projects(limit)
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/slowing-projects")
async def slowing_projects(limit: int = 10):
    """Get projects that are slowing down."""
    try:
        projects = get_slowing_projects(limit)
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")

    print(f"Starting Verra chatbot backend on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
