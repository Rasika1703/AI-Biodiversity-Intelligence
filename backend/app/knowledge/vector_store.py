"""
Retrieval layer for Darukaa.Earth.

Design goals
------------
1. Real vector retrieval (ChromaDB + sentence-transformer embeddings) when the
   environment allows it.
2. Never crash the API if Chroma or the transformer model is unavailable:
   degrade to an in-process NumPy cosine index over the same embeddings, and
   degrade the embedder to a deterministic hashing vectoriser that needs no
   model download.
3. Hybrid scoring: dense cosine similarity is blended with a lexical BM25-lite
   score and a metadata boost for the variables detected in the user's context.
   Pure dense retrieval misses exact terms like "pH 5.2" or "Faidherbia";
   pure lexical misses paraphrase. The blend is what the reasoning layer needs.
"""

from __future__ import annotations

import hashlib
import logging
import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

import numpy as np

from ..config import settings
from . import corpus

log = logging.getLogger("darukaa.retrieval")

_TOKEN_RE = re.compile(r"[a-z0-9_.]+")


def tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


# --------------------------------------------------------------------------- embedders
class HashingEmbedder:
    """Deterministic, dependency-free embedder (word + character trigram hashing).

    Not as semantically rich as a transformer, but stable, instant and offline —
    which keeps the demo alive on any machine. Used only when sentence-transformers
    is unavailable.
    """

    name = "hashing-512"
    dim = 512

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        out = np.zeros((len(list(texts := list(texts))), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            words = tokenize(text)
            for w in words:
                out[i, self._h(w) % self.dim] += 1.0
                for j in range(len(w) - 2):
                    out[i, self._h(w[j : j + 3]) % self.dim] += 0.35
            norm = np.linalg.norm(out[i])
            if norm:
                out[i] /= norm
        return out

    @staticmethod
    def _h(token: str) -> int:
        return int(hashlib.md5(token.encode()).hexdigest()[:8], 16)


class TransformerEmbedder:
    """sentence-transformers wrapper (all-MiniLM-L6-v2 by default)."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # noqa: WPS433

        self.model = SentenceTransformer(model_name)
        self.name = model_name
        self.dim = int(self.model.get_sentence_embedding_dimension())

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        vectors = self.model.encode(list(texts), normalize_embeddings=True)
        return np.asarray(vectors, dtype=np.float32)


def build_embedder():
    if settings.embedding_backend == "hashing":
        log.info("Embedding backend forced to hashing.")
        return HashingEmbedder()
    try:
        embedder = TransformerEmbedder(settings.embedding_model)
        log.info("Embedding backend: sentence-transformers/%s", settings.embedding_model)
        return embedder
    except Exception as exc:  # pragma: no cover - environment dependent
        log.warning("sentence-transformers unavailable (%s); using hashing embedder.", exc)
        return HashingEmbedder()


# --------------------------------------------------------------------------- result type
@dataclass
class Retrieved:
    doc: Dict[str, Any]
    dense: float
    lexical: float
    boost: float
    score: float
    snippet: str = field(default="")

    def as_citation(self) -> Dict[str, Any]:
        return {
            "id": self.doc["id"],
            "title": self.doc["title"],
            "source": self.doc["source"],
            "authors": self.doc["authors"],
            "year": self.doc["year"],
            "url": self.doc["url"],
            "tier": self.doc["tier"],
            "score": round(self.score, 4),
            "snippet": self.snippet or self.doc["text"][:260].rsplit(" ", 1)[0] + "…",
        }


# --------------------------------------------------------------------------- store
class KnowledgeBase:
    """Hybrid retrieval over the curated evidence corpus."""

    def __init__(self) -> None:
        self.docs = corpus.documents()
        self.embedder = build_embedder()
        self.backend = "numpy"
        self.collection = None
        self._matrix: Optional[np.ndarray] = None
        self._df: Dict[str, int] = {}
        self._doc_tokens: List[List[str]] = []
        self._avg_len = 1.0
        self._build()

    # ---------------------------------------------------------------- build
    def _build(self) -> None:
        texts = [self._doc_text(d) for d in self.docs]
        vectors = self.embedder.encode(texts)
        self._matrix = vectors
        self._index_lexical(texts)

        if not settings.use_chroma:
            log.info("Chroma disabled by configuration; using NumPy index.")
            return
        try:
            import chromadb  # noqa: WPS433
            from chromadb.config import Settings as ChromaSettings  # noqa: WPS433

            client = chromadb.PersistentClient(
                path=settings.chroma_dir,
                settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
            )
            name = f"darukaa_{self.embedder.name.replace('/', '_')}"
            try:
                client.delete_collection(name)
            except Exception:  # collection may not exist
                pass
            collection = client.create_collection(
                name=name, metadata={"hnsw:space": "cosine", "project": "darukaa-earth"}
            )
            collection.add(
                ids=[d["id"] for d in self.docs],
                embeddings=[v.tolist() for v in vectors],
                documents=texts,
                metadatas=[
                    {
                        "title": d["title"],
                        "source": d["source"],
                        "year": d["year"],
                        "tier": d["tier"],
                        "variables": ",".join(d["variables"]),
                        "biomes": ",".join(d["biomes"]),
                        "metrics": ",".join(d["metrics"]),
                    }
                    for d in self.docs
                ],
            )
            self.collection = collection
            self.backend = "chromadb"
            log.info("Chroma collection '%s' indexed with %d documents.", name, len(self.docs))
        except Exception as exc:  # pragma: no cover - environment dependent
            log.warning("ChromaDB unavailable (%s); using NumPy cosine index.", exc)

    @staticmethod
    def _doc_text(doc: Dict[str, Any]) -> str:
        return (
            f"{doc['title']}. Source: {doc['source']} ({doc['year']}). "
            f"Topics: {', '.join(doc['variables'])}. Biomes: {', '.join(doc['biomes'])}. "
            f"Metrics: {', '.join(doc['metrics'])}. {doc['text']}"
        )

    def _index_lexical(self, texts: List[str]) -> None:
        self._doc_tokens = [tokenize(t) for t in texts]
        self._avg_len = sum(len(t) for t in self._doc_tokens) / max(len(self._doc_tokens), 1)
        df: Dict[str, int] = {}
        for tokens in self._doc_tokens:
            for token in set(tokens):
                df[token] = df.get(token, 0) + 1
        self._df = df

    # ---------------------------------------------------------------- scoring
    def _bm25(self, query_tokens: List[str], idx: int, k1: float = 1.4, b: float = 0.72) -> float:
        tokens = self._doc_tokens[idx]
        if not tokens:
            return 0.0
        length = len(tokens)
        score = 0.0
        n_docs = len(self._doc_tokens)
        for token in set(query_tokens):
            tf = tokens.count(token)
            if not tf:
                continue
            df = self._df.get(token, 0)
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * length / self._avg_len))
        return score

    def _dense(self, query: str) -> np.ndarray:
        if self.collection is not None:
            try:
                qv = self.embedder.encode([query])[0]
                res = self.collection.query(
                    query_embeddings=[qv.tolist()], n_results=len(self.docs)
                )
                order = {doc_id: i for i, doc_id in enumerate(res["ids"][0])}
                distances = res["distances"][0]
                out = np.zeros(len(self.docs), dtype=np.float32)
                for i, doc in enumerate(self.docs):
                    pos = order.get(doc["id"])
                    out[i] = 1.0 - float(distances[pos]) if pos is not None else 0.0
                return out
            except Exception as exc:  # pragma: no cover
                log.warning("Chroma query failed (%s); falling back to NumPy.", exc)
        qv = self.embedder.encode([query])[0]
        assert self._matrix is not None
        return self._matrix @ qv

    # ---------------------------------------------------------------- public API
    def search(
        self,
        query: str,
        k: int = 6,
        variables: Optional[List[str]] = None,
        biomes: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
    ) -> List[Retrieved]:
        variables = [v for v in (variables or []) if v]
        biomes = [b for b in (biomes or []) if b]
        exclude = set(exclude or [])

        dense = self._dense(query)
        q_tokens = tokenize(query + " " + " ".join(variables) + " " + " ".join(biomes))
        lexical_raw = np.array([self._bm25(q_tokens, i) for i in range(len(self.docs))], dtype=np.float32)
        lexical = lexical_raw / (lexical_raw.max() or 1.0)

        results: List[Retrieved] = []
        for i, doc in enumerate(self.docs):
            if doc["id"] in exclude:
                continue
            boost = 0.0
            overlap = len(set(variables) & set(doc["variables"] + doc["metrics"]))
            boost += 0.06 * overlap
            if biomes and (set(biomes) & set(doc["biomes"])):
                boost += 0.08
            if "all" in doc["biomes"]:
                boost += 0.01
            if doc["tier"] in ("meta_analysis", "institutional"):
                boost += 0.03
            score = (
                settings.dense_weight * float(dense[i])
                + settings.lexical_weight * float(lexical[i])
                + boost
            )
            results.append(
                Retrieved(
                    doc=doc,
                    dense=float(dense[i]),
                    lexical=float(lexical[i]),
                    boost=boost,
                    score=score,
                    snippet=self._snippet(doc["text"], q_tokens),
                )
            )
        results.sort(key=lambda r: -r.score)
        return results[:k]

    @staticmethod
    def _snippet(text: str, q_tokens: List[str], width: int = 300) -> str:
        sentences = re.split(r"(?<=[.!?]) +", text)
        if not sentences:
            return text[:width]
        qs = set(q_tokens)
        best = max(sentences, key=lambda s: len(qs & set(tokenize(s))))
        idx = sentences.index(best)
        window = " ".join(sentences[idx : idx + 2])
        return window[:width].strip()

    def stats(self) -> Dict[str, Any]:
        base = corpus.stats()
        base.update(
            {
                "vector_backend": self.backend,
                "embedding_model": self.embedder.name,
                "embedding_dim": self.embedder.dim,
                "dense_weight": settings.dense_weight,
                "lexical_weight": settings.lexical_weight,
            }
        )
        return base


_kb: Optional[KnowledgeBase] = None


def get_kb() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb
