import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag.guards import check_pii, check_advice, get_advice_refusal, get_pii_refusal
from rag.assembler import generate_answer
from scheduler import start_scheduler, stop_scheduler, get_scheduler_status

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("api")


# ---------------------------------------------------------------------------
# Lifespan — startup & shutdown hooks
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting scheduler...")
    start_scheduler()
    yield
    # Shutdown
    logger.info("Stopping scheduler...")
    stop_scheduler()


app = FastAPI(title="HDFC Mutual Fund FAQ API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SourceDocument(BaseModel):
    url: str
    type: str
    scheme: str
    doc_date: str


class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    status: str
    answer: str
    citation_url: str
    last_updated: str
    source_documents: Optional[List[SourceDocument]] = None

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/scheduler/status")
def scheduler_status():
    """Return current scheduler state: running/stopped, next run time, last run result."""
    return get_scheduler_status()

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    question = request.question.strip()
    
    if check_pii(question):
        return QueryResponse(**get_pii_refusal())
    
    if check_advice(question):
        return QueryResponse(**get_advice_refusal())
    
    try:
        result = generate_answer(question)
        return QueryResponse(
            status="answered",
            answer=result['answer'],
            citation_url=result['citation_url'],
            last_updated=result['last_updated'],
            source_documents=result.get('source_documents', []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
