"""
Conversational Intelligence Layer
----------------------------------
Handles multi-turn memory, slot-filling of required environmental variables,
and generation of clarifying questions when input is incomplete. This is
deliberately separate from the reasoning/recommendation engine: this module
figures out WHAT we know and WHAT is still missing; recommendation_engine.py
decides WHAT TO DO with what we know.
"""
import re
from typing import Dict, Any, List, Optional

# The minimum set of variables required for multi-metric reasoning
# (the brief requires at least 3 environmental variables handled together).
CORE_SLOTS = ["soil_organic_carbon", "rainfall", "land_use"]

OPTIONAL_SLOTS = [
    "crop_type", "region", "soil_ph", "temperature", "pollution",
    "water_body", "habitat_diversity", "soil_moisture",
]

ALL_SLOTS = CORE_SLOTS + OPTIONAL_SLOTS

CLARIFYING_QUESTIONS = {
    "soil_organic_carbon": "What is your soil organic carbon (SOC) percentage? (e.g., 0.3%)",
    "rainfall": "How would you describe your rainfall pattern? (low / moderate / high)",
    "land_use": "What is the current land use or crop type? (e.g., monoculture wheat, agroforestry, pasture)",
    "region": "Which climatic region best describes your land? (e.g., semi-arid, tropical, temperate)",
    "crop_type": "What crop(s) are currently grown, if any?",
    "pollution": "Is there notable pesticide/fertilizer use or nearby pollution? (low / high)",
}

# Lightweight text-input parsing: regex/keyword extraction rather than
# requiring the user to always supply structured JSON.
_PATTERNS = {
    "soil_organic_carbon": re.compile(r"(?:soc|soil organic carbon)[^0-9]*(\d+(?:\.\d+)?)\s*%?", re.I),
    "soil_ph": re.compile(r"\bph[^0-9]*(\d+(?:\.\d+)?)", re.I),
    "temperature": re.compile(r"(\d+(?:\.\d+)?)\s*(?:°c|deg c|celsius)", re.I),
}

# Fallback pattern used ONLY when we're waiting on soil_organic_carbon and the
# user replies with a bare number, e.g. "10%" or "0.7" with no other context.
_BARE_NUMBER = re.compile(r"(\d+(?:\.\d+)?)\s*%?")

_KEYWORD_SLOTS = {
    "rainfall": {"low": ["low rainfall", "dry", "drought", "arid", "low rain"],
                 "high": ["high rainfall", "heavy rain", "monsoon"],
                 "moderate": ["moderate rainfall", "average rain"]},
    "land_use": {"monoculture": ["monoculture"], "agroforestry": ["agroforestry"],
                 "deforested": ["deforest", "cleared land"], "pasture": ["pasture", "grazing"],
                 "urban_adjacent": ["urban", "peri-urban"],
                 "wetland": ["wetland", "mangrove", "marsh"],
                 "invasive": ["invasive species", "invasive"],
                 "agriculture": ["agriculture", "farm", "field", "crop"]},
    "region": {"semi-arid": ["semi-arid", "semiarid"], "tropical": ["tropical"],
               "temperate": ["temperate"], "arid": ["arid"]},
    "pollution": {"high": ["pesticide", "heavy chemical", "polluted", "high pollution"],
                  "low": ["organic farming", "no chemical", "low pollution"]},
    "crop_type": {"wheat": ["wheat"], "rice": ["rice"], "maize": ["maize", "corn"],
                  "monoculture": ["monoculture"]},
    "water_body": {"present": ["river", "stream", "pond", "lake", "wetland", "water body"]},
}

# Bare single-word answers accepted directly when we're waiting on `rainfall`.
_RAINFALL_BARE = {"low": "low", "high": "high", "moderate": "moderate",
                   "medium": "moderate", "average": "moderate"}


class ConversationSession:
    """Holds per-user multi-turn memory. In production this would be backed
    by Redis / a database keyed by session_id; for this reference
    implementation it lives in-process (see app.py SESSIONS dict)."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.variables: Dict[str, Any] = {}
        self.history: List[Dict[str, str]] = []  # [{role, content}]
        self.turns = 0
        # Tracks which slot the *last* clarifying question asked about, and
        # which slots we've already asked about this session (so we never
        # ask the same question twice even if extraction keeps failing).
        self.awaiting_slot: Optional[str] = None
        self.asked_slots: set = set()

    def _try_direct_slot_answer(self, text: str) -> bool:
        """If we just asked about a specific slot, interpret a short reply as
        a direct answer to THAT slot even if it lacks the usual keywords
        (e.g. answering "10%" or "0.7" to the SOC question)."""
        if not self.awaiting_slot or self.awaiting_slot in self.variables:
            return False
        slot = self.awaiting_slot
        stripped = text.strip()
        low = stripped.lower()

        if slot == "soil_organic_carbon":
            m = _BARE_NUMBER.search(stripped)
            if m:
                self.variables[slot] = float(m.group(1))
                return True
        elif slot == "rainfall":
            first_word = re.split(r"[\s,.]", low)[0] if low else ""
            if first_word in _RAINFALL_BARE:
                self.variables[slot] = _RAINFALL_BARE[first_word]
                return True
        elif slot == "land_use":
            # Free-form: accept the raw phrase itself as the land-use description
            # if nothing more specific was already extracted.
            if 0 < len(stripped) < 60:
                self.variables[slot] = stripped
                return True
        return False

    def update_from_text(self, text: str) -> None:
        text_lower = text.lower()
        for slot, pattern in _PATTERNS.items():
            match = pattern.search(text)
            if match:
                try:
                    self.variables[slot] = float(match.group(1))
                except ValueError:
                    pass
        for slot, value_map in _KEYWORD_SLOTS.items():
            # Pick the most specific (longest) matching keyword for this slot,
            # so "semi-arid" isn't clobbered by the shorter substring "arid".
            best_value, best_len = None, -1
            for value, keywords in value_map.items():
                for kw in keywords:
                    if kw in text_lower and len(kw) > best_len:
                        best_value, best_len = value, len(kw)
            if best_value is not None:
                self.variables[slot] = best_value

        # If the structured/keyword passes above didn't resolve the slot we
        # are actively waiting on, fall back to interpreting the raw reply
        # as a direct answer to that specific question.
        if self.awaiting_slot and self.awaiting_slot not in self.variables:
            self._try_direct_slot_answer(text)

    def update_from_structured(self, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            if key in ALL_SLOTS and value is not None:
                self.variables[key] = value

    def missing_core_slots(self) -> List[str]:
        return [s for s in CORE_SLOTS if s not in self.variables]

    def next_clarifying_question(self) -> Optional[str]:
        # Prefer a core slot we haven't asked about yet, so we don't loop on
        # the same question if extraction keeps failing for one slot while
        # others remain unasked.
        missing = self.missing_core_slots()
        if not missing:
            self.awaiting_slot = None
            return None
        not_yet_asked = [s for s in missing if s not in self.asked_slots]
        slot_to_ask = not_yet_asked[0] if not_yet_asked else missing[0]
        self.asked_slots.add(slot_to_ask)
        self.awaiting_slot = slot_to_ask
        return CLARIFYING_QUESTIONS.get(slot_to_ask, f"Could you provide {slot_to_ask}?")

    def has_enough_context(self) -> bool:
        """Brief requires reasoning across >= 3 environmental variables together."""
        if len(self.variables) >= 3 and len(self.missing_core_slots()) == 0:
            self.awaiting_slot = None
            return True
        return False

    def record(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})
        if role == "user":
            self.turns += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "variables": self.variables,
            "turns": self.turns,
            "missing_core_slots": self.missing_core_slots(),
            "awaiting_slot": self.awaiting_slot,
            "history_length": len(self.history),
        }
