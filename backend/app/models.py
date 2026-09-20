"""API schemas."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ------------------------------------------------------------------ input
class SiteContext(BaseModel):
    """Structured JSON input. Every field optional — the system asks for what it needs."""

    soil_organic_carbon: Optional[float] = Field(None, description="SOC, % by mass")
    soil_ph: Optional[float] = Field(None, description="Soil pH (1-14)")
    soil_moisture: Optional[str] = Field(None, description="low | moderate | high")
    soil_texture: Optional[str] = None
    salinity_ds_m: Optional[float] = Field(None, description="Electrical conductivity, dS/m")
    land_use: Optional[str] = Field(None, description="e.g. monoculture wheat, grazing, wetland")
    crop: Optional[str] = None
    area_ha: Optional[float] = None
    region: Optional[str] = None
    biome: Optional[str] = Field(None, description="semi_arid | tropical | temperate_cropland | wetland | grassland | forest | drylands")
    rainfall_mm: Optional[float] = Field(None, description="Annual rainfall, mm")
    rainfall_pattern: Optional[str] = Field(None, description="low | erratic | seasonal | high")
    temperature_c: Optional[float] = None
    irrigation: Optional[str] = None
    tree_cover_pct: Optional[float] = None
    natural_habitat_pct: Optional[float] = Field(None, description="% semi-natural habitat in surrounding landscape")
    species_of_concern: Optional[List[str]] = None
    observed_changes: Optional[List[str]] = None
    fertiliser_kg_n_ha: Optional[float] = None
    pesticide_use: Optional[str] = Field(None, description="none | low | moderate | high")
    pollution_sources: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    goal: Optional[str] = None
    constraints: Optional[List[str]] = None


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: Optional[str] = None
    structured: Optional[SiteContext] = None
    mode: Literal["text", "structured"] = "text"
    force_analysis: bool = Field(
        False, description="Skip remaining clarifying questions and analyse with assumptions."
    )


# ------------------------------------------------------------------ output
class Citation(BaseModel):
    id: str
    title: str
    source: str
    authors: str
    year: int
    url: str
    tier: str
    score: float
    snippet: str


class MetricImpact(BaseModel):
    metric: str
    label: str
    direction: Literal["increase", "decrease", "stabilise"]
    expected_change: str
    horizon: str
    baseline: Optional[str] = None


class Recommendation(BaseModel):
    rank: int
    title: str
    what_to_do: str
    why_it_works: str
    metrics: List[MetricImpact]
    time_horizon: Literal["short", "medium", "long"]
    horizon_detail: str
    confidence: float
    confidence_label: str
    confidence_basis: str
    evidence_ids: List[str]
    interactions: List[str] = []
    watch_outs: List[str] = []
    first_actions: List[str] = []
    tags: List[str] = []


class Linkage(BaseModel):
    source: str
    target: str
    relation: str
    explanation: str
    strength: float


class ClarifyingQuestion(BaseModel):
    slot: str
    question: str
    why_it_matters: str
    options: List[str] = []
    example: Optional[str] = None


class Retrieval(BaseModel):
    query: str
    backend: str
    embedding_model: str
    chunks: List[Citation]


class ChatResponse(BaseModel):
    session_id: str
    turn: int
    kind: Literal["clarify", "analysis", "note"]
    headline: str
    message: str
    context: Dict[str, Any] = {}
    context_completeness: float = 0.0
    assumptions: List[str] = []
    questions: List[ClarifyingQuestion] = []
    recommendations: List[Recommendation] = []
    linkages: List[Linkage] = []
    citations: List[Citation] = []
    retrieval: Optional[Retrieval] = None
    metric_projection: List[Dict[str, Any]] = []
    monitoring_plan: List[Dict[str, str]] = []
    generator: str = "reasoning-engine"
    latency_ms: int = 0


class SessionSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    turns: int
    context: Dict[str, Any] = {}


class SessionDetail(SessionSummary):
    messages: List[Dict[str, Any]] = []
    asked_slots: List[str] = []
