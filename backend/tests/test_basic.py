import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from knowledge.retriever import KnowledgeRetriever
from recommendation_engine import RecommendationEngine
from conversation import ConversationSession
from app import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_retriever_structured_match():
    retriever = KnowledgeRetriever()
    docs = retriever.structured_match({"soil_organic_carbon": 0.3})
    assert len(docs) > 0
    assert all("KB" in d["id"] for d in docs)


def test_retriever_semantic_search():
    retriever = KnowledgeRetriever()
    results = retriever.semantic_search("monoculture wheat low rainfall biodiversity")
    assert len(results) > 0


def test_recommendation_engine_multi_metric():
    engine = RecommendationEngine()
    variables = {
        "soil_organic_carbon": 0.3,
        "rainfall": "low",
        "land_use": "monoculture wheat",
        "region": "semi-arid",
    }
    result = engine.generate(variables)
    assert result["recommendation_count"] > 0
    assert result["variables_considered"] >= 3
    for rec in result["recommendations"]:
        assert rec["recommendation"]
        assert rec["why_it_works"]
        assert rec["impacted_metrics"]
        assert rec["time_horizon"] in ("short", "medium", "long")
        assert rec["source"]


def test_conversation_asks_clarifying_question_when_incomplete():
    session = ConversationSession("test-session")
    session.update_from_text("Biodiversity is declining on my land")
    assert not session.has_enough_context()
    question = session.next_clarifying_question()
    assert question is not None


def test_conversation_fills_slots_from_text():
    session = ConversationSession("test-session-2")
    session.update_from_text(
        "Soil organic carbon is 0.3%, rainfall is low, monoculture wheat, semi-arid region"
    )
    assert session.has_enough_context()
    assert session.variables["soil_organic_carbon"] == 0.3
    assert session.variables["rainfall"] == "low"


def test_chat_endpoint_asks_clarifying_question():
    res = client.post("/chat", json={
        "session_id": "api-test-1",
        "message": "Biodiversity is declining on my land"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["needs_clarification"] is True
    assert data["clarifying_question"]


def test_chat_endpoint_full_flow_gives_recommendation():
    payload = {
        "session_id": "api-test-2",
        "message": "Soil organic carbon is 0.3%, rainfall is low, monoculture wheat in a semi-arid region"
    }
    res = client.post("/chat", json=payload)
    data = res.json()
    assert data["needs_clarification"] is False
    assert data["structured_result"]["recommendation_count"] > 0


def test_structured_chat_endpoint():
    payload = {
        "session_id": "api-test-3",
        "variables": {
            "soil_organic_carbon": 0.3,
            "rainfall": "low",
            "land_use": "monoculture wheat",
            "region": "semi-arid",
        }
    }
    res = client.post("/chat/structured", json=payload)
    data = res.json()
    assert data["needs_clarification"] is False
    assert len(data["structured_result"]["recommendations"]) > 0
