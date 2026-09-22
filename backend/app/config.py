"""Runtime configuration, read from environment variables (.env supported)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

try:  # optional, keeps local dev pleasant
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return default


@dataclass
class Settings:
    app_name: str = "Darukaa.Earth — AI Biodiversity Intelligence"
    version: str = "1.0.0"

    # LLM
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "").strip()
    llm_model: str = os.getenv("LLM_MODEL", "claude-sonnet-4-5-20250929")
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "2400"))
    llm_temperature: float = _float("LLM_TEMPERATURE", 0.25)

    # Retrieval
    use_chroma: bool = _bool("USE_CHROMA", True)
    chroma_dir: str = os.getenv("CHROMA_DIR", str(BASE_DIR / "data" / "chroma"))
    embedding_backend: str = os.getenv("EMBEDDING_BACKEND", "auto")  # auto | hashing
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    dense_weight: float = _float("DENSE_WEIGHT", 0.62)
    lexical_weight: float = _float("LEXICAL_WEIGHT", 0.38)
    top_k: int = int(os.getenv("TOP_K", "7"))

    # Storage
    db_path: str = os.getenv("DB_PATH", str(BASE_DIR / "data" / "darukaa.db"))

    # Server
    cors_origins: List[str] = field(
        default_factory=lambda: [
            o.strip()
            for o in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,*",
            ).split(",")
            if o.strip()
        ]
    )

    def ensure_dirs(self) -> None:
        Path(self.chroma_dir).mkdir(parents=True, exist_ok=True)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    @property
    def llm_enabled(self) -> bool:
        return bool(self.anthropic_api_key)


settings = Settings()
settings.ensure_dirs()
