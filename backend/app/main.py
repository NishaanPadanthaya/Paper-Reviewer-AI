import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Support both package and script execution
try:
    from .crew_setup import run_research_crew  # type: ignore
except Exception:
    # When executed as a script (python backend/app/main.py), adjust sys.path
    import sys, pathlib
    current_dir = pathlib.Path(__file__).resolve().parent  # .../backend/app
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    from crew_setup import run_research_crew  # type: ignore

load_dotenv()

app = FastAPI(title="PaperReviewer AI – SmartResearch using AI Agents")

# CORS for local dev (adjust as needed)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummarizeRequest(BaseModel):
    topic: str
    top_n: Optional[int] = 5


class PaperSummary(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    link: str
    published: Optional[str] = None
    summary: dict  # {problem, methodology, findings, limitations}


class SummarizeResponse(BaseModel):
    topic: str
    model: str
    papers: List[PaperSummary]


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    topic = (req.topic or "").strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic must not be empty")

    top_n = req.top_n or 5
    try:
        result = run_research_crew(topic=topic, top_n=top_n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crew execution failed: {e}")

    return result



if __name__ == "__main__":

    import uvicorn, sys, pathlib
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    backend_dir = pathlib.Path(__file__).resolve().parents[1] 
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
