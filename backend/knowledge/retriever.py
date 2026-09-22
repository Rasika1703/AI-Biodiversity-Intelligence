"""
Knowledge Retrieval Layer
--------------------------
This is the RAG layer of the system. It does NOT rely on an LLM's parametric
memory for facts. Instead, every fact used in a recommendation is retrieved
from a structured, version-controlled knowledge base (knowledge_base.json),
each entry citing a real source (FAO / IPCC / peer-reviewed study).

Retrieval strategy:
1. STRUCTURED FILTER PASS - match `trigger_conditions` against the user's
   known variable values (deterministic, explainable, auditable).
2. SEMANTIC PASS - TF-IDF cosine similarity over the `finding` +
   `intervention` text, used to catch relevant knowledge whose trigger
   conditions don't exactly match user input, or when the user asks a free
   text question rather than supplying structured variables.

We use TF-IDF (scikit-learn) rather than a downloaded embedding model
because it is fully local/offline, deterministic, and auditable -- suited to
a scientific-grounding use case where you need to explain *why* a document
was retrieved. Swapping this module for a dense-embedding + vector DB
(e.g., FAISS/Chroma + sentence-transformers) is a drop-in upgrade; the
interface (`retrieve`) would not need to change.
"""
import json
import os
from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")


class KnowledgeRetriever:
    def __init__(self, kb_path: str = KB_PATH):
        with open(kb_path, "r") as f:
            self.knowledge_base: List[Dict[str, Any]] = json.load(f)

        self._corpus = [
            f"{doc['finding']} {doc['intervention']} {doc['mechanism']} "
            f"{' '.join(doc['variables'])}"
            for doc in self.knowledge_base
        ]
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._doc_matrix = self._vectorizer.fit_transform(self._corpus)

    def _matches_trigger(self, doc: Dict[str, Any], variables: Dict[str, Any]) -> bool:
        """Deterministic structured-filter pass over trigger_conditions."""
        conditions = doc.get("trigger_conditions", {})
        if not conditions:
            return False
        for key, expected in conditions.items():
            actual = variables.get(key)
            if actual is None:
                return False
            actual_str = str(actual).lower()
            expected_str = str(expected).lower()

            if expected_str.startswith("<"):
                try:
                    threshold = float(expected_str[1:])
                    if not (float(actual) < threshold):
                        return False
                except (ValueError, TypeError):
                    return False
            elif expected_str.startswith(">"):
                try:
                    threshold = float(expected_str[1:])
                    if not (float(actual) > threshold):
                        return False
                except (ValueError, TypeError):
                    return False
            else:
                if expected_str not in actual_str and actual_str not in expected_str:
                    return False
        return True

    def structured_match(self, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Pass 1: exact/deterministic condition matching against known variables."""
        return [doc for doc in self.knowledge_base if self._matches_trigger(doc, variables)]

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Pass 2: TF-IDF cosine-similarity semantic retrieval for free-text queries."""
        if not query.strip():
            return []
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._doc_matrix).flatten()
        ranked_idx = scores.argsort()[::-1][:top_k]
        results = []
        for idx in ranked_idx:
            if scores[idx] > 0.05:
                doc = dict(self.knowledge_base[idx])
                doc["_similarity_score"] = round(float(scores[idx]), 3)
                results.append(doc)
        return results

    def retrieve(self, variables: Dict[str, Any], free_text: str = "", top_k: int = 5) -> List[Dict[str, Any]]:
        """Combined retrieval: structured matches first (guaranteed relevant),
        topped up with semantic matches, de-duplicated, ranked."""
        structured = self.structured_match(variables)
        structured_ids = {d["id"] for d in structured}

        semantic = self.semantic_search(free_text or self._variables_to_query(variables), top_k=top_k)
        semantic_unique = [d for d in semantic if d["id"] not in structured_ids]

        combined = structured + semantic_unique
        return combined[:top_k] if top_k else combined

    @staticmethod
    def _variables_to_query(variables: Dict[str, Any]) -> str:
        return " ".join(f"{k} {v}" for k, v in variables.items() if v is not None)
