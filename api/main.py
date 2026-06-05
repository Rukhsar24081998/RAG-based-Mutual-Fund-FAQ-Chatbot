from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag.guards import check_pii, check_advice, get_advice_refusal, get_pii_refusal
from rag.assembler import generate_answer

app = FastAPI(title="HDFC Mutual Fund FAQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    status: str
    answer: str
    citation_url: str
    last_updated: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

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
            last_updated=result['last_updated']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
