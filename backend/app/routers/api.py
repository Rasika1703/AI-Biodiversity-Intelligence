"""HTTP surface."""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query

from ..config import settings
from ..knowledge import corpus
from ..knowledge.vector_store import get_kb
from ..models import ChatRequest, ChatResponse, SessionDetail, SessionSummary
from ..services import clarify
from ..services.advisor import handle
from ..services.session_store import store

router = APIRouter(prefix="/api")


# ------------------------------------------------------------------ health
@router.get("/health")
def health() -> Dict[str, Any]:
    kb = get_kb()
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version,
        "llm": {"enabled": settings.llm_enabled, "model": settings.llm_model if settings.llm_enabled else None},
        "knowledge": kb.stats(),
    }


# ------------------------------------------------------------------ chat
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    if not request.message and not request.structured:
        raise HTTPException(status_code=422, detail="Provide a message, structured site data, or both.")
    return handle(request)


# ------------------------------------------------------------------ sessions
@router.get("/sessions", response_model=List[SessionSummary])
def list_sessions(limit: int = Query(40, ge=1, le=200)) -> List[SessionSummary]:
    return [SessionSummary(**s) for s in store.list(limit)]


@router.post("/sessions", response_model=SessionSummary)
def create_session() -> SessionSummary:
    session_id = store.create()
    data = store.get(session_id)
    return SessionSummary(
        id=data["id"],
        title=data["title"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        turns=0,
        context={},
    )


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(session_id: str) -> SessionDetail:
    data = store.get(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionDetail(
        id=data["id"],
        title=data["title"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        turns=sum(1 for m in data["messages"] if m["role"] == "user"),
        context=data["context"],
        messages=data["messages"],
        asked_slots=data["asked_slots"],
    )


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str) -> Dict[str, str]:
    if not store.get(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    store.delete(session_id)
    return {"status": "deleted", "session_id": session_id}


# ------------------------------------------------------------------ knowledge
@router.get("/knowledge/stats")
def knowledge_stats() -> Dict[str, Any]:
    return get_kb().stats()


@router.get("/knowledge/search")
def knowledge_search(
    q: str = Query(..., min_length=2),
    k: int = Query(6, ge=1, le=20),
) -> Dict[str, Any]:
    """Transparent retrieval endpoint: shows dense, lexical and boost components."""
    hits = get_kb().search(q, k=k)
    return {
        "query": q,
        "backend": get_kb().backend,
        "embedding_model": get_kb().embedder.name,
        "results": [
            {
                **h.as_citation(),
                "components": {
                    "dense": round(h.dense, 4),
                    "lexical": round(h.lexical, 4),
                    "metadata_boost": round(h.boost, 4),
                },
                "variables": h.doc["variables"],
                "metrics": h.doc["metrics"],
            }
            for h in hits
        ],
    }


@router.get("/knowledge/documents")
def knowledge_documents() -> Dict[str, Any]:
    return {
        "count": len(corpus.documents()),
        "documents": [
            {
                "id": d["id"],
                "title": d["title"],
                "source": d["source"],
                "authors": d["authors"],
                "year": d["year"],
                "url": d["url"],
                "tier": d["tier"],
                "variables": d["variables"],
                "metrics": d["metrics"],
                "biomes": d["biomes"],
                "excerpt": d["text"][:220].rsplit(" ", 1)[0] + "…",
            }
            for d in corpus.documents()
        ],
    }


@router.get("/knowledge/documents/{doc_id}")
def knowledge_document(doc_id: str) -> Dict[str, Any]:
    doc = corpus.by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


# ------------------------------------------------------------------ metrics
@router.get("/metrics/{session_id}")
def session_metrics(session_id: str) -> Dict[str, Any]:
    data = store.get(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    last_analysis = next(
        (
            m["payload"]
            for m in reversed(data["messages"])
            if m["role"] == "assistant" and m.get("payload", {}) and m["payload"].get("kind") == "analysis"
        ),
        None,
    )
    return {
        "session_id": session_id,
        "context": data["context"],
        "completeness": clarify.completeness(data["context"]),
        "asked_slots": data["asked_slots"],
        "documents_used": store.cited_docs(session_id),
        "projection": (last_analysis or {}).get("metric_projection", []),
        "linkages": (last_analysis or {}).get("linkages", []),
        "monitoring_plan": (last_analysis or {}).get("monitoring_plan", []),
        "recommendations": [
            {
                "rank": r["rank"],
                "title": r["title"],
                "time_horizon": r["time_horizon"],
                "confidence": r["confidence"],
            }
            for r in (last_analysis or {}).get("recommendations", [])
        ],
    }


@router.get("/schema/site-context")
def site_context_schema() -> Dict[str, Any]:
    """Field list for the structured-JSON input mode in the UI."""
    from ..models import SiteContext

    return SiteContext.model_json_schema()
