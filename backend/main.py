from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from backend.rag_engine import HybridRAGEngine
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify environment structure
os.makedirs("frontend", exist_ok=True)

app = FastAPI(title="NUST Offline Admissions FAQ Bot")

from typing import List, Dict, Optional

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    query: str
    history: List[Message] = []

class QueryResponse(BaseModel):
    answer: str
    citations: list
    confidence_status: str

# Instantiate the Offline RAG Engine globally
# This holds the LLM, FAISS index, and BM25 matrix in memory
try:
    engine = HybridRAGEngine(data_dir=os.path.join(os.path.dirname(__file__), '..', 'data'),
                             models_dir=os.path.join(os.path.dirname(__file__), '..', 'models'))
    logger.info("HybridRAGEngine initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Engine: {e}")
    # Don't crash so we can still serve the static files, but engine will be none

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    try:
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]
        response_data = engine.query(request.query, history=history_dicts)
        return QueryResponse(
            answer=response_data['answer'],
            citations=response_data['citations'],
            confidence_status=response_data['confidence_status']
        )
    except Exception as e:
        logger.error(f"Error during query processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend to be statically served
frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
