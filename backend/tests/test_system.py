"""End-to-end checks for extraction, anti-repetition, retrieval and reasoning."""

from __future__ import annotations

import os

os.environ.setdefault("DB_PATH", "./data/test_darukaa.db")
os.environ.setdefault("USE_CHROMA", "false")

from app.knowledge import corpus  # noqa: E402
from app.knowledge.vector_store import get_kb  # noqa: E402
from app.services import clarify, extraction, reasoning  # noqa: E402

RICH = (
    "I farm 40 ha of monoculture wheat in semi-arid Rajasthan. Soil organic carbon is 0.3% "
    "and pH is 8.4, rainfall is about 420 mm and erratic. Native bees are disappearing and "
    "I spray pesticide moderately. Tree cover is 3%."
)


# ------------------------------------------------------------------ corpus
def test_corpus_is_indexed_and_typed():
    docs = corpus.documents()
    assert len(docs) >= 40
    for doc in docs:
        assert doc["id"] and doc["title"] and doc["source"]
        assert doc["year"] >= 1990
        assert doc["variables"] and doc["metrics"]
        assert len(doc["text"]) > 200
    assert len({d["id"] for d in docs}) == len(docs)


# ------------------------------------------------------------------ extraction
def test_extraction_pulls_multiple_variables():
    ctx = extraction.extract(RICH)
    assert ctx["soil_organic_carbon"] == 0.3
    assert ctx["soil_ph"] == 8.4
    assert ctx["rainfall_mm"] == 420
    assert ctx["area_ha"] == 40
    assert ctx["biome"] == "semi_arid"
    assert "monoculture" in ctx["land_use"]
    assert ctx["crop"] == "wheat"


def test_merge_accumulates_without_losing_prior_context():
    first = extraction.extract("My soil organic carbon is 0.4%.")
    second = extraction.extract("Rainfall is low and I graze cattle.")
    merged = extraction.merge(first, second)
    assert merged["soil_organic_carbon"] == 0.4
    assert merged["rainfall_pattern"] == "low"


# ------------------------------------------------------------------ clarify
def test_clarifier_never_repeats_an_asked_slot():
    ctx = extraction.extract("Biodiversity is declining on my land.")
    first = clarify.next_questions(ctx, asked=[])
    assert first
    asked = [q["slot"] for q in first]
    second = clarify.next_questions(ctx, asked=asked)
    assert all(q["slot"] not in asked for q in second)


def test_clarifier_stops_once_core_context_is_known():
    ctx = extraction.extract(RICH)
    assert clarify.completeness(ctx) > 0.6
    assert clarify.should_ask(ctx, asked=[], turn=1) is False


def test_clarifier_gives_up_after_a_few_turns():
    ctx = extraction.extract("Biodiversity is declining on my land.")
    assert clarify.should_ask(ctx, asked=[], turn=1) is True
    assert clarify.should_ask(ctx, asked=[], turn=4) is False


def test_unanswered_questions_become_stated_assumptions():
    ctx = extraction.extract("Biodiversity is declining on my land.")
    asked = [q["slot"] for q in clarify.next_questions(ctx, asked=[])]
    notes = clarify.assumptions(ctx, asked)
    assert notes and all(isinstance(n, str) for n in notes)


# ------------------------------------------------------------------ retrieval
def test_hybrid_retrieval_returns_relevant_scored_documents():
    kb = get_kb()
    hits = kb.search("semi-arid low soil organic carbon monoculture wheat pollinators", k=6)
    assert len(hits) == 6
    scores = [h.score for h in hits]
    assert scores == sorted(scores, reverse=True)
    assert hits[0].score > 0
    citation = hits[0].as_citation()
    assert citation["id"] and citation["source"]


def test_retrieval_respects_variable_filter():
    kb = get_kb()
    hits = kb.search("improve soil carbon", k=5, variables=["soil_organic_carbon"])
    assert any("soil_organic_carbon" in h.doc["variables"] for h in hits)


# ------------------------------------------------------------------ reasoning
def _recommend(ctx):
    return reasoning.recommend(ctx, clarify.completeness(ctx))


def test_recommendations_are_evidence_backed_and_multi_metric():
    ctx = extraction.extract(RICH)
    engine = _recommend(ctx)
    recs = engine["recommendations"]
    assert 3 <= len(recs) <= 5
    for rec in recs:
        assert rec["what_to_do"] and rec["why_it_works"]
        assert rec["evidence_ids"], "every recommendation must cite at least one document"
        assert all(corpus.by_id(doc_id) for doc_id in rec["evidence_ids"])
        assert rec["time_horizon"] in {"short", "medium", "long"}
        assert 0 < rec["confidence"] <= 1
        assert rec["confidence_label"] in {"high", "moderate", "indicative"}
        assert len(rec["metrics"]) >= 2, "single-variable answers are not acceptable"


def test_confidence_is_lower_when_the_site_is_unknown():
    rich = _recommend(extraction.extract(RICH))["recommendations"]
    vague = _recommend(extraction.extract("Biodiversity is declining on my land."))[
        "recommendations"
    ]
    assert max(r["confidence"] for r in vague) < max(r["confidence"] for r in rich)


def test_linkages_connect_multiple_variables():
    ctx = extraction.extract(RICH)
    engine = _recommend(ctx)
    links = engine["linkages"]
    assert len(links) >= 2
    for link in links:
        assert link["source"] and link["target"] and link["explanation"]
    joined = " ".join(r["why_it_works"] for r in engine["recommendations"]).lower()
    assert sum(term in joined for term in ("soil", "water", "habitat", "species")) >= 3


def test_projection_has_horizons_and_basis():
    ctx = extraction.extract(RICH)
    projection = _recommend(ctx)["projection"]
    assert projection
    for row in projection:
        assert row["metric"] and row["basis"]
        assert "year_3" in row
