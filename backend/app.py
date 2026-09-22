"""
Darukaa.Earth Biodiversity Intelligence Chatbot - API entrypoint.

Run locally:
    uvicorn app:app --reload --port 8000

Endpoints:
    POST /chat              text input, multi-turn, session-memory aware
    POST /chat/structured   structured JSON input (+ optional geo-coords)
    GET  /session/{id}      inspect session memory (debug/demo aid)
    GET  /health            liveness probe
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from models import ChatRequest, StructuredChatRequest, ChatResponse
from conversation import ConversationSession
from recommendation_engine import RecommendationEngine

app = FastAPI(
    title="Darukaa.Earth Biodiversity Intelligence Chatbot",
    description="Knowledge-grounded conversational system for biodiversity "
                 "and environmental reasoning.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RecommendationEngine()

# In-memory session store for this reference implementation.
# Swap for Redis/Postgres-backed store for production/multi-instance deploy.
SESSIONS: dict[str, ConversationSession] = {}


def get_session(session_id: str) -> ConversationSession:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = ConversationSession(session_id)
    return SESSIONS[session_id]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session = get_session(req.session_id)
    session.record("user", req.message)
    session.update_from_text(req.message)

    if not session.has_enough_context():
        question = session.next_clarifying_question()
        reply = (
            "Thanks for sharing that. To give you a grounded, multi-metric "
            f"recommendation I need a bit more information. {question}"
            if session.variables else
            f"I'd like to help. {question}"
        )
        session.record("assistant", reply)
        return ChatResponse(
            session_id=req.session_id,
            reply=reply,
            needs_clarification=True,
            clarifying_question=question,
            known_variables=session.variables,
        )

    result = engine.generate(session.variables, free_text=req.message)
    reply = engine.format_for_chat(result)
    session.record("assistant", reply)
    return ChatResponse(
        session_id=req.session_id,
        reply=reply,
        needs_clarification=False,
        known_variables=session.variables,
        structured_result=result,
    )


@app.post("/chat/structured", response_model=ChatResponse)
def chat_structured(req: StructuredChatRequest):
    session = get_session(req.session_id)
    if req.message:
        session.record("user", req.message)
        session.update_from_text(req.message)
    session.update_from_structured(req.variables)

    if req.latitude is not None and req.longitude is not None:
        session.variables["latitude"] = req.latitude
        session.variables["longitude"] = req.longitude

    if not session.has_enough_context():
        question = session.next_clarifying_question()
        reply = f"A few more details would sharpen the analysis. {question}"
        session.record("assistant", reply)
        return ChatResponse(
            session_id=req.session_id,
            reply=reply,
            needs_clarification=True,
            clarifying_question=question,
            known_variables=session.variables,
        )

    result = engine.generate(session.variables, free_text=req.message or "")
    reply = engine.format_for_chat(result)
    session.record("assistant", reply)
    return ChatResponse(
        session_id=req.session_id,
        reply=reply,
        needs_clarification=False,
        known_variables=session.variables,
        structured_result=result,
    )


@app.get("/session/{session_id}")
def inspect_session(session_id: str):
    session = get_session(session_id)
    return session.to_dict()


# Serve the minimal demo frontend (not the focus of the challenge, but
# useful for a live demo link).
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/static", StaticFiles(directory=_frontend_dir), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(_frontend_dir, "index.html"))
