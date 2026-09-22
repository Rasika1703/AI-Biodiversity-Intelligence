from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Client-generated session id for multi-turn memory")
    message: str = Field(..., description="Free-text user message")


class StructuredChatRequest(BaseModel):
    session_id: str
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured environmental variables, e.g. "
                     "{'soil_organic_carbon': 0.3, 'rainfall': 'low', "
                     "'land_use': 'monoculture wheat', 'region': 'semi-arid'}"
    )
    message: Optional[str] = Field(default="", description="Optional accompanying free-text")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    needs_clarification: bool
    clarifying_question: Optional[str] = None
    known_variables: Dict[str, Any]
    structured_result: Optional[Dict[str, Any]] = None
