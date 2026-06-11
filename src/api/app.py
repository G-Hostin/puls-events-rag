import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException

from src.api.schemas import (
    AskRequest,
    AskResponse,
    HealthResponse,
    RebuildResponse,
    Source,
)
from src.data.openagenda_client import fetch_events
from src.data.preprocessing import process
from src.rag.chain import build_chain
from src.rag.prompt import format_documents
from src.vectorstore.chunking import chunk_documents
from src.vectorstore.event_to_document import event_to_document
from src.vectorstore.indexing import build_index

load_dotenv()
logger = logging.getLogger("uvicorn.error")

REGION = "Nouvelle-Aquitaine"
DAYS_HISTORY = 365
EVENTS_PATH = Path("data/events.jsonl")
INDEX_DIR = Path("data/index")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if INDEX_DIR.exists() and any(INDEX_DIR.iterdir()):
        try:
            app.state.chain, app.state.retriever = build_chain()
            logger.info("Chaine RAG chargee avec succes")
        except Exception as e:
            logger.warning(f"Index present mais chargement echoue : {e}")
            app.state.chain, app.state.retriever = None, None
    else:
        logger.warning("Index FAISS absent : appelez POST /rebuild pour initialiser")
        app.state.chain, app.state.retriever = None, None
    yield


app = FastAPI(
    title="Puls-Events RAG API",
    description="API d'assistant pour la recommandation d'evenements culturels en Nouvelle-Aquitaine",
    version="1.0.0",
    lifespan=lifespan,
)


def verify_admin_key(x_api_key: str = Header(...)):
    expected = os.getenv("ADMIN_API_KEY")
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Cle API admin invalide")


@app.get("/health", response_model=HealthResponse)
def health():
    """Verifie que l'API est operationnelle"""
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    """Pose une question au systeme RAG et retourne une reponse augmentee"""
    if app.state.chain is None:
        raise HTTPException(
            status_code=503,
            detail="Index FAISS non initialise. Appelez POST /rebuild d'abord",
        )

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="La question ne peut pas etre vide")

    try:
        sources = app.state.retriever.invoke(question)
        answer_text = app.state.chain.invoke({
            "context": format_documents(sources),
            "question": question,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la generation : {e}")

    return {
        "answer": answer_text,
        "sources": [
            Source(
                uid=s.metadata.get("uid"),
                title=s.metadata.get("title"),
                city=s.metadata.get("city"),
                url=s.metadata.get("url"),
            )
            for s in sources
        ],
    }


@app.post(
    "/rebuild",
    response_model=RebuildResponse,
    dependencies=[Depends(verify_admin_key)],
)
def rebuild():
    """
    Rafraichit les donnees OpenAgenda et reconstruit l'index FAISS
    Endpoint protege par header X-API-Key
    """
    date_min = (datetime.now() - timedelta(days=DAYS_HISTORY)).strftime("%Y-%m-%d")
    raw = fetch_events(REGION, date_min)
    events = process(raw)

    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS_PATH.open("w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    documents = [event_to_document(e) for e in events]
    chunks = chunk_documents(documents)
    build_index(chunks, INDEX_DIR)

    app.state.chain, app.state.retriever = build_chain()

    return {
        "status": "ok",
        "events_fetched": len(events),
        "chunks_indexed": len(chunks),
    }