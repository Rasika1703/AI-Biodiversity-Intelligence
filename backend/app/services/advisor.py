"""Orchestration: one request in, one grounded analysis out."""

from __future__ import annotations

import time
from typing import Any, Dict, List

from ..knowledge import corpus
from ..knowledge.vector_store import get_kb
from ..models import ChatRequest, ChatResponse
from . import clarify, extraction, llm, reasoning
from .session_store import store

PRETTY = {
    "soil_organic_carbon": "soil organic carbon",
    "soil_ph": "soil pH",
    "rainfall_mm": "annual rainfall",
    "rainfall_pattern": "rainfall pattern",
    "land_use": "land use",
    "biome": "climate zone",
    "natural_habitat_pct": "semi-natural habitat share",
    "area_ha": "area",
    "tree_cover_pct": "tree cover",
    "pesticide_use": "pesticide use",
    "species_of_concern": "species of concern",
    "salinity_ds_m": "salinity (EC)",
    "fertiliser_kg_n_ha": "nitrogen rate",
    "irrigation": "water source",
    "observed_changes": "observed changes",
    "pollution_sources": "pollution sources",
    "latitude": "latitude",
    "longitude": "longitude",
}

UNITS = {
    "soil_organic_carbon": "%",
    "rainfall_mm": " mm",
    "area_ha": " ha",
    "tree_cover_pct": "%",
    "natural_habitat_pct": "%",
    "salinity_ds_m": " dS/m",
    "temperature_c": " °C",
    "fertiliser_kg_n_ha": " kg N/ha",
}


def summarise_context(ctx: Dict[str, Any], limit: int = 6) -> str:
    parts: List[str] = []
    for key, value in ctx.items():
        if value in (None, "", [], {}) or key in {"constraints", "goal"}:
            continue
        label = PRETTY.get(key, key.replace("_", " "))
        if isinstance(value, list):
            rendered = ", ".join(str(v) for v in value[:3])
        else:
            rendered = f"{value}{UNITS.get(key, '')}"
        parts.append(f"{label} {rendered}")
        if len(parts) >= limit:
            break
    return "; ".join(parts)


def build_query(ctx: Dict[str, Any], message: str) -> str:
    bits = [message or ""]
    for key in ["land_use", "biome", "crop", "region", "goal", "irrigation"]:
        if ctx.get(key):
            bits.append(str(ctx[key]))
    if ctx.get("soil_organic_carbon") is not None:
        bits.append(f"soil organic carbon {ctx['soil_organic_carbon']}% degraded soil restoration")
    if str(ctx.get("rainfall_pattern") or "") in {"low", "erratic", "seasonal"}:
        bits.append("water limited rainfed water harvesting infiltration")
    if ctx.get("natural_habitat_pct") is not None and float(ctx["natural_habitat_pct"]) < 20:
        bits.append("habitat fragmentation connectivity semi-natural habitat pollinators")
    if ctx.get("species_of_concern"):
        bits.append("species decline " + " ".join(str(s) for s in ctx["species_of_concern"]))
    if ctx.get("pollution_sources"):
        bits.append("pollution nutrient load water quality " + " ".join(str(s) for s in ctx["pollution_sources"]))
    return " ".join(b for b in bits if b).strip()[:900]


def title_for(ctx: Dict[str, Any], message: str) -> str:
    if ctx.get("land_use") and ctx.get("biome"):
        return f"{str(ctx['biome']).replace('_', '-')} {ctx['land_use']}".title()[:60]
    if ctx.get("land_use"):
        return str(ctx["land_use"]).title()[:60]
    text = (message or "New analysis").strip().replace("\n", " ")
    return (text[:57] + "…") if len(text) > 58 else text


def handle(request: ChatRequest) -> ChatResponse:
    started = time.perf_counter()
    session_id = store.ensure(request.session_id)
    session = store.get(session_id) or {}
    turn = store.next_turn(session_id)

    # ---------------------------------------------------------------- 1. context
    context: Dict[str, Any] = dict(session.get("context") or {})
    user_text = (request.message or "").strip()
    if request.structured:
        context = extraction.merge(context, request.structured.model_dump(exclude_none=True))
    if user_text:
        context = extraction.merge(context, extraction.extract(user_text))

    display_text = user_text or "Structured site data submitted."
    store.add_message(session_id, turn, "user", display_text, {"structured": bool(request.structured)})
    store.save_context(session_id, context)
    if turn == 1 or (session.get("title") in (None, "New analysis")):
        store.set_title(session_id, title_for(context, user_text))

    asked: List[str] = list(session.get("asked_slots") or [])
    completeness = clarify.completeness(context)

    # ---------------------------------------------------------------- 2. clarify?
    wants_analysis = request.force_analysis or bool(
        user_text and any(w in user_text.lower() for w in ["analyse", "analyze", "just tell", "go ahead", "recommend now", "skip"])
    )
    if not wants_analysis and clarify.should_ask(context, asked, turn):
        questions = clarify.next_questions(context, asked, limit=2)
        if questions:
            store.mark_asked(session_id, [q["slot"] for q in questions])
            known = summarise_context(context)
            narration = llm.clarify_message(context, questions, known)
            response = ChatResponse(
                session_id=session_id,
                turn=turn,
                kind="clarify",
                headline="Two variables away from a useful answer" if len(questions) > 1 else "One variable away from a useful answer",
                message=narration["text"],
                context=context,
                context_completeness=completeness,
                questions=questions,
                generator=narration["generator"],
                latency_ms=int((time.perf_counter() - started) * 1000),
            )
            store.add_message(session_id, turn, "assistant", response.message, response.model_dump())
            return response

    # ---------------------------------------------------------------- 3. retrieve
    kb = get_kb()
    query = build_query(context, user_text)
    variables = [k for k, v in context.items() if v not in (None, "", [], {})]
    biomes = [context["biome"]] if context.get("biome") else []
    hits = kb.search(query, k=7, variables=variables, biomes=biomes)
    citations = [h.as_citation() for h in hits]
    store.log_retrieval(session_id, turn, query, citations)

    # ---------------------------------------------------------------- 4. reason
    engine = reasoning.recommend(context, completeness, limit=5)
    recommendations = engine["recommendations"]

    # Attach the evidence each recommendation actually depends on, pulling in any
    # cited document that retrieval did not surface so no card is left unsupported.
    cited_ids = {c["id"] for c in citations}
    for rec in recommendations:
        for doc_id in rec["evidence_ids"]:
            if doc_id in cited_ids:
                continue
            doc = corpus.by_id(doc_id)
            if not doc:
                continue
            citations.append(
                {
                    "id": doc["id"],
                    "title": doc["title"],
                    "source": doc["source"],
                    "authors": doc["authors"],
                    "year": doc["year"],
                    "url": doc["url"],
                    "tier": doc["tier"],
                    "score": 0.0,
                    "snippet": doc["text"][:260].rsplit(" ", 1)[0] + "\u2026",
                }
            )
            cited_ids.add(doc["id"])

    assumptions = clarify.assumptions(context, asked)
    narration = llm.narrate(
        context,
        engine["diagnosis"],
        recommendations,
        citations,
        assumptions,
        store.history(session_id, limit=8),
    )

    remaining = clarify.next_questions(context, asked, limit=1)
    if remaining:
        store.mark_asked(session_id, [q["slot"] for q in remaining])

    response = ChatResponse(
        session_id=session_id,
        turn=turn,
        kind="analysis",
        headline=reasoning.headline(context, engine["diagnosis"], recommendations),
        message=narration["text"],
        context=context,
        context_completeness=completeness,
        assumptions=assumptions,
        questions=remaining,
        recommendations=recommendations,
        linkages=engine["linkages"],
        citations=citations,
        retrieval={
            "query": query,
            "backend": kb.backend,
            "embedding_model": kb.embedder.name,
            "chunks": [h.as_citation() for h in hits],
        },
        metric_projection=engine["projection"],
        monitoring_plan=engine["monitoring"],
        generator=narration["generator"],
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
    store.add_message(session_id, turn, "assistant", response.message, response.model_dump())
    return response
