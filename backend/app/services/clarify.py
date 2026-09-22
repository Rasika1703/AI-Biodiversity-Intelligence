"""
Clarifying-question engine.

Two rules make this feel like a scientist rather than a form:

1. A slot is asked at most once per session, ever. `asked_slots` in the session
   store is the ledger; anything already in it is filtered out even if the user
   ignored the question. Unanswered slots become explicit assumptions.
2. Questions are ranked by how much they would change the recommendation, not by
   field order, and only slots that are *relevant to the described situation* are
   eligible (nobody is asked about grazing rest periods on a wetland).
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

Context = Dict[str, Any]


def _is_crop(ctx: Context) -> bool:
    lu = (ctx.get("land_use") or "").lower()
    return any(w in lu for w in ["crop", "agrofor", "paddy", "plantation", "fallow"]) or bool(ctx.get("crop"))


def _is_water_system(ctx: Context) -> bool:
    return (ctx.get("biome") in {"wetland", "riparian", "coastal"}) or "wetland" in (ctx.get("land_use") or "")


def _is_grazing(ctx: Context) -> bool:
    return "graz" in (ctx.get("land_use") or "") or ctx.get("biome") == "grassland"


def _is_forest(ctx: Context) -> bool:
    return ctx.get("biome") in {"forest", "tropical"} or "deforest" in (ctx.get("land_use") or "")


SLOTS: List[Dict[str, Any]] = [
    {
        "slot": "land_use",
        "priority": 100,
        "question": "What is the land currently used for?",
        "why": "Land use sets which interventions are even possible and which habitat baseline applies.",
        "options": ["Monoculture cropland", "Mixed cropping", "Grazing land", "Wetland", "Forest / regrowth", "Degraded or fallow"],
        "relevant": lambda ctx: True,
    },
    {
        "slot": "biome",
        "priority": 95,
        "question": "Which climate zone is the site in?",
        "why": "Rainfall regime decides whether water partitioning or nutrient cycling is the binding constraint.",
        "options": ["Semi-arid", "Arid / dryland", "Tropical humid", "Temperate", "Wetland", "Grassland"],
        "relevant": lambda ctx: True,
    },
    {
        "slot": "soil_organic_carbon",
        "priority": 90,
        "question": "What is your soil organic carbon, as a percentage?",
        "why": "SOC drives water holding capacity, nutrient cycling and soil biodiversity all at once — it is the single most informative soil number.",
        "options": ["Below 0.5%", "0.5-1%", "1-2%", "Above 2%", "Not measured"],
        "example": "e.g. 0.3%",
        "relevant": lambda ctx: not _is_water_system(ctx),
    },
    {
        "slot": "rainfall_pattern",
        "priority": 85,
        "question": "What is the rainfall like — annual total, or simply low, erratic or reliable?",
        "why": "Water availability caps what any vegetation intervention can deliver and sets realistic timelines.",
        "options": ["Low (<600 mm)", "Erratic", "Seasonal monsoon", "High (>1100 mm)"],
        "relevant": lambda ctx: True,
    },
    {
        "slot": "natural_habitat_pct",
        "priority": 78,
        "question": "Roughly what share of the surrounding landscape is semi-natural habitat — hedges, scrub, woodlots, uncultivated margins?",
        "why": "Below about 20% natural cover, species loss accelerates non-linearly, and local measures behave very differently above and below that line.",
        "options": ["Almost none", "Under 10%", "10-20%", "Over 20%"],
        "relevant": lambda ctx: not _is_forest(ctx),
    },
    {
        "slot": "crop",
        "priority": 72,
        "question": "Which crop or crops do you grow, and in what rotation?",
        "why": "Rotation sequence determines pathogen build-up, nitrogen balance and pollinator dependence.",
        "options": [],
        "relevant": _is_crop,
    },
    {
        "slot": "soil_ph",
        "priority": 66,
        "question": "Do you know the soil pH?",
        "why": "pH is the strongest single predictor of soil bacterial community composition and controls phosphorus availability.",
        "options": ["Below 5.5 (acidic)", "5.5-7.5", "Above 7.5 (alkaline)", "Not measured"],
        "relevant": lambda ctx: not _is_water_system(ctx),
    },
    {
        "slot": "pesticide_use",
        "priority": 62,
        "question": "How much pesticide is used on or near the site?",
        "why": "Chemical load is the fastest-reversing pressure on invertebrates; habitat work underperforms while exposure continues.",
        "options": ["None", "Low / threshold-based", "Moderate", "High / calendar spraying"],
        "relevant": lambda ctx: _is_crop(ctx) or bool(ctx.get("species_of_concern")),
    },
    {
        "slot": "species_of_concern",
        "priority": 58,
        "question": "Are there particular species or groups you have noticed changing — bees, birds, fish, earthworms?",
        "why": "Indicator taxa point to the limiting resource: nesting, forage, water or connectivity.",
        "options": ["Pollinators", "Birds", "Fish / amphibians", "Soil fauna", "Not sure"],
        "relevant": lambda ctx: True,
    },
    {
        "slot": "irrigation",
        "priority": 55,
        "question": "Is the land rainfed or irrigated, and from what source?",
        "why": "Irrigation source changes salinity risk, water-table behaviour and which water measures pay back.",
        "options": ["Rainfed", "Canal / flood", "Groundwater", "Drip / sprinkler"],
        "relevant": lambda ctx: _is_crop(ctx),
    },
    {
        "slot": "area_ha",
        "priority": 48,
        "question": "How large is the area, in hectares?",
        "why": "Area sets field-interior distance, which decides whether perimeter habitat can reach the middle of the block.",
        "options": [],
        "relevant": lambda ctx: True,
    },
    {
        "slot": "salinity_ds_m",
        "priority": 45,
        "question": "Have you seen salt crusting, or do you have an EC reading?",
        "why": "Salinity changes the species palette entirely and makes leaching or biodrainage the first move.",
        "options": ["No salt problem", "Visible crusting", "Have an EC reading", "Not sure"],
        "relevant": lambda ctx: ctx.get("biome") in {"drylands", "semi_arid", "irrigated"}
        or ctx.get("irrigation") in {"flood / canal", "groundwater"},
    },
    {
        "slot": "pollution_sources",
        "priority": 42,
        "question": "Is anything entering the site from outside — fertiliser runoff, effluent, sewage, waste?",
        "why": "External loading has to be addressed at the source, otherwise on-site restoration keeps getting reset.",
        "options": ["Fertiliser runoff", "Industrial effluent", "Sewage", "Nothing obvious"],
        "relevant": lambda ctx: _is_water_system(ctx) or bool(ctx.get("observed_changes")),
    },
    {
        "slot": "tree_cover_pct",
        "priority": 40,
        "question": "How much tree or shrub cover is on the land now?",
        "why": "Existing woody cover decides whether to protect regrowth or establish new structure, which differ hugely in cost.",
        "options": ["None", "Scattered trees", "10-30%", "Over 30%"],
        "relevant": lambda ctx: not _is_water_system(ctx),
    },
    {
        "slot": "goal",
        "priority": 36,
        "question": "What outcome matters most to you over the next three years?",
        "why": "Ranking changes with the objective — carbon, pollination, water security and yield stability favour different first moves.",
        "options": ["Soil and carbon", "Pollinators and wildlife", "Water security", "Yield stability", "Credit / certification readiness"],
        "relevant": lambda ctx: True,
    },
    {
        "slot": "constraints",
        "priority": 30,
        "question": "Any constraints I should plan around — budget, labour, tenure, water rights?",
        "why": "Constraints decide staging: which measures go in year one and which wait.",
        "options": ["Limited budget", "Limited labour", "Short lease / tenure", "No major constraint"],
        "relevant": lambda ctx: True,
    },
]

CORE_SLOTS = ["land_use", "biome", "soil_organic_carbon", "rainfall_pattern", "natural_habitat_pct"]

ASSUMPTION_TEXT: Dict[str, Callable[[Context], str]] = {
    "soil_organic_carbon": lambda ctx: (
        "Soil organic carbon unknown — assumed 0.4-0.8% (typical for degraded "
        f"{(ctx.get('biome') or 'cropland').replace('_', ' ')} soils per FAO/ISRIC baselines)."
    ),
    "soil_ph": lambda ctx: "Soil pH unknown — assumed near-neutral (6.0-7.5); recheck before any liming or gypsum spend.",
    "rainfall_pattern": lambda ctx: "Rainfall pattern unknown — treated as seasonal and variable, so water-retention measures are staged first.",
    "natural_habitat_pct": lambda ctx: "Surrounding semi-natural habitat unknown — assumed a simplified landscape (under 20%), where local habitat work gives the largest gain.",
    "pesticide_use": lambda ctx: "Pesticide regime unknown — assumed moderate conventional use; the input-reduction step is included but ranked conservatively.",
    "area_ha": lambda ctx: "Area unknown — spacing guidance is given per 100 m of field interior so it scales to any block size.",
    "crop": lambda ctx: "Crop sequence unknown — rotation advice is given by functional group rather than by named crop.",
    "irrigation": lambda ctx: "Water source unknown — assumed rainfed, which is the more constraining case.",
    "species_of_concern": lambda ctx: "No indicator taxa named — the plan uses generalist proxies (wild bees, ground beetles, earthworms) for monitoring.",
    "tree_cover_pct": lambda ctx: "Existing woody cover unknown — assumed sparse, so structure-building measures are included.",
    "goal": lambda ctx: "No single objective stated — recommendations are ranked for combined biodiversity and production resilience.",
    "constraints": lambda ctx: "No constraints given — staging assumes a modest budget with 10-20% of area committed in year one.",
    "land_use": lambda ctx: "Land use not stated — advice is framed for mixed working land.",
    "biome": lambda ctx: "Climate zone not stated — assumed seasonally dry conditions.",
    "salinity_ds_m": lambda ctx: "Salinity not assessed — assumed non-saline; a quick EC test is in the monitoring plan.",
    "pollution_sources": lambda ctx: "No external loading reported — assumed none beyond on-site inputs.",
}


def filled(ctx: Context) -> List[str]:
    return [k for k, v in (ctx or {}).items() if v not in (None, "", [], {})]


def completeness(ctx: Context) -> float:
    have = set(filled(ctx))
    core = sum(1 for s in CORE_SLOTS if s in have) / len(CORE_SLOTS)
    extra_slots = [s["slot"] for s in SLOTS if s["slot"] not in CORE_SLOTS]
    extra = sum(1 for s in extra_slots if s in have) / max(len(extra_slots), 1)
    return round(min(1.0, 0.72 * core + 0.28 * extra), 3)


def next_questions(ctx: Context, asked: List[str], limit: int = 2) -> List[Dict[str, Any]]:
    """Highest-value slots that are missing, relevant and never asked before."""
    have = set(filled(ctx))
    asked_set = set(asked or [])
    candidates = [
        s
        for s in SLOTS
        if s["slot"] not in have and s["slot"] not in asked_set and s["relevant"](ctx)
    ]
    candidates.sort(key=lambda s: -s["priority"])
    return [
        {
            "slot": s["slot"],
            "question": s["question"],
            "why_it_matters": s["why"],
            "options": s.get("options", []),
            "example": s.get("example"),
        }
        for s in candidates[:limit]
    ]


def should_ask(ctx: Context, asked: List[str], turn: int) -> bool:
    """Ask only while it would genuinely change the answer."""
    have = set(filled(ctx))
    core_known = sum(1 for s in CORE_SLOTS if s in have)
    if turn >= 4:
        return False
    if core_known >= 4:
        return False
    return bool(next_questions(ctx, asked))


def assumptions(ctx: Context, asked: List[str]) -> List[str]:
    """Stated assumptions for everything asked-but-unanswered, plus unasked core gaps."""
    have = set(filled(ctx))
    gaps = [s for s in asked if s not in have]
    for slot in CORE_SLOTS:
        if slot not in have and slot not in gaps:
            gaps.append(slot)
    out = []
    for slot in gaps:
        builder = ASSUMPTION_TEXT.get(slot)
        if builder:
            out.append(builder(ctx))
    return out[:6]
