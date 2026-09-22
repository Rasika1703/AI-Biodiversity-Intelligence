"""
Turn free text into the same structured site context that the JSON input produces.

Everything downstream (reasoning, retrieval, follow-up questions) works on one
canonical dictionary, so text and JSON inputs are genuinely interchangeable.
Extraction is rule-based and deterministic — it runs before any LLM call, so the
system still understands the user when no API key is configured.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

NUM = r"(-?\d+(?:\.\d+)?)"

BIOME_PATTERNS: List[Tuple[str, str]] = [
    (r"semi[\s-]?arid|semiarid", "semi_arid"),
    (r"\barid\b|desert|dryland", "drylands"),
    (r"tropical|rainforest|equatorial", "tropical"),
    (r"temperate", "temperate_cropland"),
    (r"wetland|marsh|swamp|mangrove|peat", "wetland"),
    (r"grassland|savanna|rangeland|pasture|steppe|prairie", "grassland"),
    (r"forest|woodland|jungle", "forest"),
    (r"riparian|riverbank|streamside|floodplain", "riparian"),
    (r"coastal|estuar", "coastal"),
    (r"sub[\s-]?tropical", "subtropical"),
    (r"irrigat", "irrigated"),
]

LAND_USE_PATTERNS: List[Tuple[str, str]] = [
    (r"monoculture|mono[\s-]?crop|single crop|continuous (wheat|maize|corn|rice|soy)", "monoculture cropland"),
    (r"intercrop|mixed crop|polyculture|rotation", "diversified cropland"),
    (r"orchard|plantation|vineyard|tea estate|coffee", "perennial plantation"),
    (r"graz|livestock|cattle|sheep|goat|ranch", "grazing land"),
    (r"paddy|rice field", "rice paddy"),
    (r"fallow|abandoned|degraded land|barren|wasteland", "degraded / fallow land"),
    (r"deforest|logg|clear[\s-]?cut|slash and burn", "recently deforested land"),
    (r"wetland|marsh|swamp", "wetland"),
    (r"restor|rewild|afforest|reforest", "restoration site"),
    (r"urban|peri[\s-]?urban|city|park", "urban / peri-urban land"),
    (r"agroforest|silvopast", "agroforestry"),
]

CROP_WORDS = [
    "wheat", "rice", "maize", "corn", "soy", "soybean", "cotton", "sugarcane", "millet",
    "sorghum", "barley", "chickpea", "pigeon pea", "groundnut", "mustard", "canola",
    "coffee", "tea", "banana", "mango", "apple", "grape", "tomato", "potato", "onion",
    "blueberry", "almond", "cassava", "oil palm", "rubber", "pulses", "vegetables",
]

SPECIES_HINTS = [
    "bee", "bees", "pollinator", "pollinators", "butterfly", "butterflies", "bird", "birds",
    "amphibian", "frog", "fish", "earthworm", "beetle", "bat", "deer", "elephant", "tiger",
    "otter", "crane", "heron", "dragonfly", "moth", "spider", "snake", "orchid",
]

OBSERVED_PATTERNS: List[Tuple[str, str]] = [
    (r"declin|disappear|fewer|loss of|losing|vanish", "declining populations reported"),
    (r"yield (drop|declin|fall|reduc)|lower yields?|yields? (are )?fall", "yield decline reported"),
    (r"erosion|gully|topsoil loss|wash(ed|ing) away", "visible soil erosion"),
    (r"crust|compact|hardpan|hard soil", "surface crusting or compaction"),
    (r"waterlogg|flood", "waterlogging or flooding"),
    (r"drought|dry spell|water stress|wilting", "drought or water stress"),
    (r"salin|salt|white crust", "salinity symptoms"),
    (r"pest outbreak|infestation|locust|borer|aphid", "pest outbreaks"),
    (r"weed|invasive|lantana|parthenium|water hyacinth", "weed or invasive pressure"),
    (r"algal bloom|eutroph|green water", "eutrophication signs"),
    (r"fragment|patchy|isolated patches|corridor", "habitat fragmentation"),
]

POLLUTION_PATTERNS: List[Tuple[str, str]] = [
    (r"pesticid|insecticid|herbicid|spray", "pesticide load"),
    (r"fertilis|fertiliz|urea|nitrogen runoff|npk", "fertiliser runoff"),
    (r"industr|effluent|factory|tannery|mine|mining", "industrial effluent"),
    (r"sewage|wastewater|domestic waste", "untreated wastewater"),
    (r"plastic|solid waste|dump", "solid waste"),
    (r"smoke|burning|stubble burn", "biomass burning"),
]

GOAL_PATTERNS: List[Tuple[str, str]] = [
    (r"pollinat", "recover pollinator populations"),
    (r"soil|carbon|organic matter|fertility", "rebuild soil health and carbon"),
    (r"water|irrigat|drought|moisture", "improve water security"),
    (r"species|wildlife|habitat|biodivers", "raise biodiversity and habitat quality"),
    (r"yield|productiv|income|profit", "maintain or improve production"),
    (r"carbon credit|offset|mrv|certification", "carbon or biodiversity credit readiness"),
    (r"restor|rewild", "restore degraded land"),
]


def _find_float(text: str, patterns: List[str]) -> Optional[float]:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                continue
    return None


def extract(text: str) -> Dict[str, Any]:
    """Extract a partial site context from a free-text message."""
    if not text:
        return {}
    low = text.lower()
    out: Dict[str, Any] = {}

    # --- soil organic carbon --------------------------------------------------
    soc = _find_float(
        low,
        [
            rf"(?:soil )?organic carbon(?:\s*(?:is|of|:|=|at))?\s*{NUM}\s*%",
            rf"soc(?:\s*(?:is|of|:|=|at))?\s*{NUM}\s*%?",
            rf"{NUM}\s*%\s*(?:soil )?organic (?:carbon|matter)",
            rf"organic matter(?:\s*(?:is|of|:|=|at))?\s*{NUM}\s*%",
        ],
    )
    if soc is not None and 0 <= soc <= 30:
        if re.search(rf"organic matter[^%]{{0,12}}{soc}", low) and soc > 3:
            soc = round(soc * 0.58, 2)  # organic matter → carbon
        out["soil_organic_carbon"] = soc
    if soc is None:
        if re.search(
            r"\blow soil organic carbon\b|"
            r"\blow organic carbon\b|"
            r"\bpoor soil organic carbon\b|"
            r"\bdeclining soil carbon\b|"
            r"\blow soil carbon\b",
            low,
        ):
            out["soil_organic_carbon"] = "low"

    # --- pH -------------------------------------------------------------------
    ph = _find_float(low, [rf"ph(?:\s*(?:is|of|:|=|at|value))?\s*{NUM}", rf"{NUM}\s*ph\b"])
    if ph is not None and 2 <= ph <= 12:
        out["soil_ph"] = ph

    # --- rainfall -------------------------------------------------------------
    rain = _find_float(
        low,
        [
            rf"rainfall(?:\s*(?:is|of|:|=|around|about|approx\.?|roughly|nearly|only|averages?)){{0,3}}\s*{NUM}\s*mm",
            rf"{NUM}\s*mm\s*(?:of\s*)?(?:[a-z]+\s+){{0,2}}rain",
            rf"precipitation(?:\s*(?:is|of|:|=|around|about|roughly)){{0,3}}\s*{NUM}\s*mm",
        ],
    )

    qualitative = None
    if re.search(
        r"low rainfall|scanty rain|little rain|poor rain|deficit rain|rain[- ]?fed and dry"
        r"|rainfall(?:\s+(?:is|was|:|=))?\s+(?:very\s+)?low|rain(?:fall)?\s*:\s*low",
        low,
    ):
        qualitative = "low"
    elif re.search(r"erratic|unpredictable rain|irregular rain|delayed monsoon|variable rain", low):
        qualitative = "erratic"
    elif re.search(r"heavy rain|high rainfall|monsoon[- ]fed|abundant rain", low):
        qualitative = "high"
    elif re.search(r"seasonal rain|single (rainy|wet) season", low):
        qualitative = "seasonal"

    if rain is not None:
        out["rainfall_mm"] = rain
    if qualitative:
        
        out["rainfall_pattern"] = qualitative
    elif rain is not None:
        out["rainfall_pattern"] = "low" if rain < 600 else ("moderate" if rain < 1100 else "high")

    # --- temperature ----------------------------------------------------------
    temp = _find_float(
        low,
        [
            rf"temperature(?:\s*(?:is|of|:|=|around|about))?\s*{NUM}\s*(?:deg|°|c\b)",
            rf"{NUM}\s*(?:deg\s*c|°c)\b",
        ],
    )
    if temp is not None and -20 <= temp <= 60:
        out["temperature_c"] = temp

    # --- area, salinity, inputs, cover ---------------------------------------
    area = _find_float(low, [rf"{NUM}\s*(?:ha|hectare|hectares)\b", rf"{NUM}\s*acres?\b"])
    if area is not None:
        if re.search(rf"{area}\s*acres?", low):
            area = round(area * 0.4047, 2)
        out["area_ha"] = area

    ec = _find_float(low, [rf"{NUM}\s*ds/?m", rf"(?:ec|conductivity)(?:\s*(?:is|of|:|=))?\s*{NUM}"])
    if ec is not None and 0 <= ec <= 60:
        out["salinity_ds_m"] = ec

    nitrogen = _find_float(low, [rf"{NUM}\s*kg\s*(?:of\s*)?n(?:itrogen)?\s*(?:per|/)\s*(?:ha|hectare)"])
    if nitrogen is not None:
        out["fertiliser_kg_n_ha"] = nitrogen

    tree = _find_float(low, [rf"{NUM}\s*%\s*(?:tree|canopy|forest)\s*cover", rf"tree cover(?:\s*(?:is|of|:|=))?\s*{NUM}\s*%"])
    if tree is not None:
        out["tree_cover_pct"] = tree

    natural = _find_float(
        low,
        [
            rf"{NUM}\s*%\s*(?:semi[- ]?natural|natural habitat|native vegetation)",
            rf"(?:semi[- ]?natural|natural habitat)[^.]{{0,20}}{NUM}\s*%",
        ],
    )
    if natural is not None:
        out["natural_habitat_pct"] = natural

        # --- practical constraints -----------------------------------------------
    # These are conversational constraints, not environmental site variables.
    # They are stored in session context so later turns can use them.

    lease_years = _find_float(
        low,
        [
            rf"{NUM}\s*(?:year|years|yr|yrs)\s*(?:left|remaining|left on the lease)",
            rf"lease(?:\s*(?:is|of|for|has))?\s*{NUM}\s*(?:year|years|yr|yrs)",
            rf"{NUM}\s*(?:year|years|yr|yrs)\s*(?:lease|rental)",
        ],
    )

    if lease_years is not None and 0 < lease_years <= 100:
        out["lease_years_remaining"] = lease_years

    if re.search(
        r"cannot afford|can't afford|cant afford|very low budget|low budget|"
        r"limited budget|tight budget|budget is low|little money|"
        r"not afford expensive|avoid expensive|expensive interventions",
        low,
    ):
        out["budget_constraint"] = "low"

    elif re.search(
        r"moderate budget|some budget|reasonable budget|moderate cost",
        low,
    ):
        out["budget_constraint"] = "moderate"

    elif re.search(
        r"unlimited budget|budget is not a concern|cost is not a concern|"
        r"cost is no issue|money is not an issue",
        low,
    ):
        out["budget_constraint"] = "high"

    if re.search(
        r"cannot plant trees|can't plant trees|cant plant trees|"
        r"no trees|trees are not possible|tree planting is not possible|"
        r"cannot do agroforestry|can't do agroforestry|cant do agroforestry",
        low,
    ):
        out["tree_planting_constraint"] = True
    # --- coordinates ----------------------------------------------------------
    geo = re.search(rf"{NUM}\s*[,/ ]\s*{NUM}", low)
    if geo and re.search(r"lat|coord|gps|location|\bat\b", low):
        try:
            lat, lon = float(geo.group(1)), float(geo.group(2))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                out["latitude"], out["longitude"] = lat, lon
        except ValueError:
            pass

    # --- categorical ----------------------------------------------------------
    for pattern, value in BIOME_PATTERNS:
        if re.search(pattern, low):
            out["biome"] = value
            break
    for pattern, value in LAND_USE_PATTERNS:
        if re.search(pattern, low):
            out["land_use"] = value
            break

    crops = [c for c in CROP_WORDS if re.search(rf"\b{re.escape(c)}s?\b", low)]
    if crops:
        out["crop"] = ", ".join(dict.fromkeys(crops))[:80]

    if re.search(r"\bno irrigation|rain[- ]?fed|rainfed\b", low):
        out["irrigation"] = "rainfed"
    elif re.search(r"drip", low):
        out["irrigation"] = "drip"
    elif re.search(r"flood irrigat|canal|furrow", low):
        out["irrigation"] = "flood / canal"
    elif re.search(r"borewell|tube ?well|groundwater", low):
        out["irrigation"] = "groundwater"

    if re.search(r"heavy (pesticide|spray)|spray (weekly|every)|high pesticide", low):
        out["pesticide_use"] = "high"
    elif re.search(r"pesticid|insecticid|herbicid", low):
        out["pesticide_use"] = "moderate"
    elif re.search(r"no pesticid|organic|chemical[- ]free|zero[- ]budget", low):
        out["pesticide_use"] = "none"

    if re.search(r"\bdry soil|moisture is low|soil is dry|low moisture", low):
        out["soil_moisture"] = "low"
    elif re.search(r"waterlogg|saturated soil|high moisture", low):
        out["soil_moisture"] = "high"

    for texture in ["sandy loam", "silt loam", "clay loam", "sandy", "clayey", "clay", "loam", "silty", "gravelly", "black cotton", "laterite", "alluvial"]:
        if texture in low:
            out["soil_texture"] = texture
            break

    species = [s for s in SPECIES_HINTS if re.search(rf"\b{s}\b", low)]
    if species:
        out["species_of_concern"] = list(dict.fromkeys(species))[:8]

    observed = [label for pattern, label in OBSERVED_PATTERNS if re.search(pattern, low)]
    if observed:
        out["observed_changes"] = observed

    pollution = [label for pattern, label in POLLUTION_PATTERNS if re.search(pattern, low)]
    if pollution:
        out["pollution_sources"] = pollution

    goals = [label for pattern, label in GOAL_PATTERNS if re.search(pattern, low)]
    if goals:
        out["goal"] = goals[0]

    region = re.search(
        r"\b(?:in|near|at|from)\s+(?:(?:the|a|an|my)\s+)?(?:[a-z][a-z-]*\s+){0,2}"
        r"((?:North|South|East|West|Central)?\s?[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?)",
        text,
    )
    if region:
        candidate = region.group(1).strip()
        if candidate.lower() not in {"i", "my", "the", "it"} and len(candidate) > 2:
            out["region"] = candidate

    return out


def merge(existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """Later turns override earlier ones; list fields accumulate without duplicates."""
    merged = dict(existing or {})
    for key, value in (new or {}).items():
        if value in (None, "", [], {}):
            continue
        if isinstance(value, list):
            current = merged.get(key) or []
            merged[key] = list(dict.fromkeys([*current, *value]))
        else:
            merged[key] = value
    return merged
