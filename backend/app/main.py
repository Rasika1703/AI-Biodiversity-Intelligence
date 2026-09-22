"""Darukaa.Earth API — AI biodiversity intelligence."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .knowledge.vector_store import get_kb
from .routers.api import router
from .services.session_store import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
log = logging.getLogger("darukaa")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    kb = get_kb()  # builds embeddings + index once, at boot
    log.info(
        "Knowledge base ready — %s documents, backend=%s, embeddings=%s",
        kb.stats()["document_count"],
        kb.backend,
        kb.embedder.name,
    )
    log.info("LLM narration: %s", "enabled" if settings.llm_enabled else "disabled (reasoning engine only)")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=(
        "Retrieval-augmented environmental reasoning. A curated evidence corpus is indexed with hybrid "
        "dense + lexical retrieval; a deterministic reasoning engine diagnoses binding constraints and ranks "
        "interventions; an LLM narrates the result without inventing facts."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse(
        {
            "name": settings.app_name,
            "version": settings.version,
            "docs": "/docs",
            "health": "/api/health",
        }
    )
