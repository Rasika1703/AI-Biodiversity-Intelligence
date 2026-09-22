"""
The reasoning engine.

This is what makes the system an environmental scientist rather than a prompt.
It runs before and independently of the LLM:

  context  ->  diagnosis (which constraints bind, and how they interact)
           ->  candidate interventions scored against the diagnosis
           ->  evidence lookup for each surviving candidate
           ->  metric projection, confidence and staging

The LLM is then given the engine's output plus retrieved evidence and asked only
to narrate it. If no API key is present the engine's output is rendered directly,
so the product never degrades into a generic chatbot.

Every intervention declares the *interactions* it participates in, which is how
multi-variable reasoning becomes explicit rather than implied: soil carbon is
linked to water holding, water holding to species survival, habitat share to
pollination and pest control, chemical load to invertebrate recovery.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

Context = Dict[str, Any]

# --------------------------------------------------------------------------- helpers
METRIC_LABELS = {
    "soil_organic_carbon": "Soil organic carbon",
    "water_holding_capacity": "Plant-available water",
    "infiltration": "Water infiltration",
    "microbial_diversity": "Soil microbial diversity",
    "earthworm_density": "Earthworm density",
    "species_richness": "Species richness",
    "pollinator_abundance": "Wild pollinator abundance",
    "natural_enemy_abundance": "Natural enemy abundance",
    "pest_control": "Natural pest regulation",
    "habitat_connectivity": "Habitat connectivity",
    "habitat_diversity": "Habitat structural diversity",
    "erosion": "Soil erosion",
    "nitrate_removal": "Nitrate interception",
    "water_quality": "Water quality",
    "carbon_sequestration": "Carbon sequestration",
    "yield": "Crop yield",
    "yield_stability": "Yield stability",
    "salinity": "Root-zone salinity",
    "soil_ph": "Soil pH",
    "nitrogen": "Soil nitrogen",
    "pesticide_risk": "Pesticide risk load",
    "vegetation_cover": "Vegetation cover",
    "water_productivity": "Water productivity",
    "freshwater_species_richness": "Freshwater species richness",
    "hydrological_function": "Hydrological function",
    "forest_cover": "Woody cover",
    "disease_pressure": "Soil-borne disease pressure",
    "net_benefit": "Net economic benefit",
}

HORIZON_DETAIL = {
    "short": "0-12 months",
    "medium": "1-3 years",
    "long": "3-10 years",
}


def _num(ctx: Context, key: str, default: Optional[float] = None) -> Optional[float]:
    value = ctx.get(key)
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _text(ctx: Context, *keys: str) -> str:
    return " ".join(str(ctx.get(k) or "") for k in keys).lower()


def _has(ctx: Context, key: str, *needles: str) -> bool:
    value = str(ctx.get(key) or "").lower()
    return any(n in value for n in needles)


def _list_has(ctx: Context, key: str, *needles: str) -> bool:
    values = " ".join(str(v).lower() for v in (ctx.get(key) or []))
    return any(n in values for n in needles)


# --------------------------------------------------------------------------- diagnosis
def diagnose(ctx: Context) -> Dict[str, Any]:
    """Identify the binding constraints and the couplings between them."""
    soc = _num(ctx, "soil_organic_carbon")
    ph = _num(ctx, "soil_ph")
    rain = _num(ctx, "rainfall_mm")
    pattern = str(ctx.get("rainfall_pattern") or "").lower()
    natural = _num(ctx, "natural_habitat_pct")
    trees = _num(ctx, "tree_cover_pct")
    ec = _num(ctx, "salinity_ds_m")

    flags: Dict[str, bool] = {
        "soc_critical": soc is not None and soc < 0.6,
        "soc_low": soc is not None and soc < 1.2,
        "soc_unknown": soc is None,
        "acidic": ph is not None and ph < 5.5,
        "alkaline": ph is not None and ph > 8.2,
        "water_limited": (rain is not None and rain < 700) or pattern in {"low", "erratic", "seasonal"},
        "water_erratic": pattern == "erratic",
        "water_excess": (rain is not None and rain > 1500) or _has(ctx, "soil_moisture", "high"),
        "simplified_landscape": natural is not None and natural < 20,
        "cleared_landscape": natural is not None and natural < 2,
        "low_tree_cover": trees is not None and trees < 10,
        "saline": (ec is not None and ec > 4) or _list_has(ctx, "observed_changes", "salinity"),
        "monoculture": _has(ctx, "land_use", "monoculture") or _has(ctx, "crop", "wheat, ") is False and _has(ctx, "land_use", "monoculture"),
        "grazing": _has(ctx, "land_use", "graz") or ctx.get("biome") == "grassland",
        "wetland": ctx.get("biome") in {"wetland", "riparian", "coastal"} or _has(ctx, "land_use", "wetland"),
        "forest": ctx.get("biome") in {"forest", "tropical"} or _has(ctx, "land_use", "deforest", "restoration"),
        "cropland": _has(ctx, "land_use", "crop", "paddy", "plantation", "agrofor", "fallow") or bool(ctx.get("crop")),
        "high_chemical": _has(ctx, "pesticide_use", "high", "moderate"),
        "high_nitrogen": (_num(ctx, "fertiliser_kg_n_ha") or 0) > 120,
        "pollinator_concern": _list_has(ctx, "species_of_concern", "bee", "pollinat", "butterfly", "moth")
        or _has(ctx, "goal", "pollinator"),
        "erosion": _list_has(ctx, "observed_changes", "erosion", "crusting"),
        "fragmentation": _list_has(ctx, "observed_changes", "fragment") or (natural is not None and natural < 10),
        "external_pollution": bool(ctx.get("pollution_sources")),
        "yield_decline": _list_has(ctx, "observed_changes", "yield"),
        "pest_outbreak": _list_has(ctx, "observed_changes", "pest"),
        "eutrophic": _list_has(ctx, "observed_changes", "eutroph"),
        "fish_amphibian": _list_has(ctx, "species_of_concern", "fish", "frog", "amphibian", "otter", "dragonfly"),
        "birds": _list_has(ctx, "species_of_concern", "bird", "crane", "heron"),
        "soil_fauna": _list_has(ctx, "species_of_concern", "earthworm", "beetle"),
        "irrigated": _has(ctx, "irrigation", "canal", "flood", "groundwater", "drip"),
        "shallow_water_table": _has(ctx, "irrigation", "canal", "flood") and (ec or 0) > 2,
    }
    if _has(ctx, "land_use", "monoculture"):
        flags["monoculture"] = True

    # Couplings: the statements that justify multi-variable reasoning.
    couplings: List[Dict[str, Any]] = []
    if flags["soc_critical"] or flags["soc_low"] or flags["soc_unknown"]:
        couplings.append(
            {
                "source": "soil_organic_carbon",
                "target": "water_holding_capacity",
                "relation": "drives",
                "strength": 0.9,
                "explanation": (
                    "Each 1% of soil organic matter holds roughly 15-20 mm more plant-available water per metre of "
                    "profile, so the carbon deficit is also a water deficit before any rain falls."
                ),
            }
        )
        couplings.append(
            {
                "source": "soil_organic_carbon",
                "target": "microbial_diversity",
                "relation": "drives",
                "strength": 0.82,
                "explanation": (
                    "Carbon is the energy substrate for the soil food web; below roughly 1% SOC the fungal and "
                    "faunal community narrows even where fertiliser keeps total biomass up."
                ),
            }
        )
    if flags["water_limited"]:
        couplings.append(
            {
                "source": "water_holding_capacity",
                "target": "species_richness",
                "relation": "limits",
                "strength": 0.85,
                "explanation": (
                    "In rainfed semi-arid systems only 15-30% of rainfall is transpired; the dry-season water gap, "
                    "not the annual total, determines which plants, invertebrates and birds persist."
                ),
            }
        )
    if flags["simplified_landscape"] or flags["fragmentation"]:
        couplings.append(
            {
                "source": "habitat_connectivity",
                "target": "pollinator_abundance",
                "relation": "limits",
                "strength": 0.88,
                "explanation": (
                    "Pollinator visitation halves at roughly 600 m from natural habitat and most solitary bees forage "
                    "within 150-600 m, so patch spacing caps pollination regardless of what is planted."
                ),
            }
        )
        couplings.append(
            {
                "source": "habitat_connectivity",
                "target": "pest_control",
                "relation": "drives",
                "strength": 0.74,
                "explanation": (
                    "Natural enemies respond to field-scale structure rather than landscape cover, so predator access "
                    "to the field interior is a separate constraint from pollinator forage."
                ),
            }
        )
    if flags["monoculture"]:
        couplings.append(
            {
                "source": "land_use",
                "target": "disease_pressure",
                "relation": "drives",
                "strength": 0.7,
                "explanation": (
                    "Continuous single-species cropping accumulates host-specific pathogens and nematodes, producing "
                    "negative plant-soil feedback that depresses yield independently of nutrient status."
                ),
            }
        )
    if flags["high_chemical"] or flags["pollinator_concern"]:
        couplings.append(
            {
                "source": "pesticide_risk",
                "target": "pollinator_abundance",
                "relation": "limits",
                "strength": 0.8,
                "explanation": (
                    "Chronic sublethal exposure suppresses invertebrate recovery; populations rebound within 1-3 "
                    "generations once exposure stops, which makes input reduction the fastest-acting lever available."
                ),
            }
        )
    if flags["wetland"] or flags["external_pollution"] or flags["eutrophic"]:
        couplings.append(
            {
                "source": "water_quality",
                "target": "freshwater_species_richness",
                "relation": "limits",
                "strength": 0.86,
                "explanation": (
                    "Catchment nutrient and sediment loading resets in-site restoration; only 30-40% of in-channel "
                    "projects improve biodiversity while upstream drivers persist."
                ),
            }
        )
    if flags["saline"]:
        couplings.append(
            {
                "source": "salinity",
                "target": "vegetation_cover",
                "relation": "limits",
                "strength": 0.8,
                "explanation": (
                    "Capillary rise from a shallow water table concentrates salts in the root zone, so cover "
                    "establishment fails until the water table is drawn down."
                ),
            }
        )
    couplings.append(
        {
            "source": "vegetation_cover",
            "target": "soil_organic_carbon",
            "relation": "feeds back",
            "strength": 0.68,
            "explanation": (
                "Root exudates and litter from continuous living cover are the main carbon input pathway, closing the "
                "loop: cover builds carbon, carbon holds water, water sustains cover."
            ),
        }
    )
    return {"flags": flags, "couplings": couplings}


# --------------------------------------------------------------------------- interventions
def _m(metric: str, direction: str, change: str, horizon: str, baseline: Optional[str] = None) -> Dict[str, Any]:
    return {
        "metric": metric,
        "label": METRIC_LABELS.get(metric, metric.replace("_", " ").title()),
        "direction": direction,
        "expected_change": change,
        "horizon": horizon,
        "baseline": baseline,
    }


Score = Callable[[Dict[str, bool], Context], float]

INTERVENTIONS: List[Dict[str, Any]] = [
    {
        "key": "legume_cover",
        "title": "Legume-based cover cropping with full residue retention",
        "what": (
            "Sow a multi-species cover mix (a legume such as cowpea, sunn hemp or berseem plus a deep-rooted "
            "brassica and a grass) into the fallow window immediately after harvest, terminate by rolling or grazing "
            "rather than ploughing, and leave 100% of residue on the surface. Start on 15-20% of the area in year one."
        ),
        "why": (
            "Cover crops add a mean 0.32 t C/ha/yr to topsoil, which in a soil starting under 1% SOC is a 15-25% "
            "relative gain in 2-4 years. The legume fixes 30-100 kg N/ha, substituting purchased nitrogen, while the "
            "surface residue cuts evaporative loss and feeds the detritivore food web that earthworms and ground "
            "beetles depend on. The carbon gain is simultaneously a water gain, which is why it ranks first in "
            "water-limited systems rather than as a soil-only measure."
        ),
        "metrics": [
            _m("soil_organic_carbon", "increase", "+15-25% relative (≈0.3 t C/ha/yr)", "medium"),
            _m("water_holding_capacity", "increase", "+15-20 mm per m of profile per 1% organic matter", "medium"),
            _m("microbial_diversity", "increase", "measurable shift in 2-3 seasons", "medium"),
            _m("nitrogen", "increase", "+30-100 kg N/ha/yr biologically fixed", "short"),
        ],
        "horizon": "medium",
        "evidence": ["POEPLAU-DON-2015", "FAO-SOC-2017", "LAL-2004-SCIENCE", "BARDGETT-2014-NATURE"],
        "interactions": [
            "Carbon gain raises plant-available water, which is the actual constraint in low-rainfall years.",
            "Residue cover lowers soil temperature and evaporation, extending the window for soil fauna activity.",
            "Fixed nitrogen reduces fertiliser demand, lowering downstream nitrate loading.",
        ],
        "watch_outs": [
            "In water-limited years a cover crop can deplete stored soil moisture — terminate early, at flowering, and keep residue in place.",
            "Carbon gains reverse within 2-3 seasons if tillage or residue removal resumes.",
        ],
        "first_actions": [
            "Take a baseline SOC and bulk density sample from 0-15 cm and 15-30 cm at five georeferenced points.",
            "Source a 3-species mix with at least one legume; budget 12-20 kg/ha seed.",
            "Pick the 15-20% of area with the lowest yield as the year-one block.",
        ],
        "tags": ["soil", "water", "carbon"],
        "score": lambda f, c: (
            2.6
            + (1.4 if f["soc_critical"] else 0.9 if f["soc_low"] else 0.5 if f["soc_unknown"] else 0)
            + (0.7 if f["cropland"] else -1.6)
            + (0.5 if f["water_limited"] else 0)
            + (0.4 if f["monoculture"] else 0)
            + (0.3 if f["erosion"] else 0)
            - (2.4 if f["wetland"] else 0)
        ),
    },
    {
        "key": "parkland_agroforestry",
        "title": "Scattered-tree parkland agroforestry using reverse-phenology species",
        "what": (
            "Establish or protect 30-60 stems/ha of nitrogen-fixing, reverse-phenology trees (Faidherbia albida "
            "where adapted, otherwise Prosopis cineraria, Acacia senegal or Gliricidia) in the cropped field itself, "
            "not only on boundaries. Where seedlings are expensive, use farmer-managed natural regeneration: protect "
            "and prune existing rootstock rather than planting."
        ),
        "why": (
            "Agroforestry raises soil organic carbon by about 21% and total soil nitrogen by 46%, cuts erosion by "
            "half and increases infiltration by 60% relative to treeless cropland. Reverse-phenology species drop "
            "nitrogen-rich litter at the onset of rains and shed leaves during grain fill, so they add fertility and "
            "midday shade without competing for light when the crop needs it — associated cereal yields rise 6-56%. "
            "The canopy also creates a 2-5 degree C cooler understorey microclimate, which extends invertebrate "
            "activity through the hottest part of the season."
        ),
        "metrics": [
            _m("soil_organic_carbon", "increase", "+21% mean vs treeless cropland", "long"),
            _m("infiltration", "increase", "+60%", "medium"),
            _m("erosion", "decrease", "-50%", "medium"),
            _m("habitat_diversity", "increase", "vertical structure for birds and cavity nesters", "long"),
            _m("yield", "increase", "+6-56% for cereals under parkland canopy", "long"),
        ],
        "horizon": "long",
        "evidence": ["KUYAH-2019-AGROFOR", "ZOMER-2016-SCIREP", "IPCC-SRCCL-2019", "SMITH-2019-GCB"],
        "interactions": [
            "Shade lowers evaporative demand, compounding the water benefit of higher soil carbon.",
            "Tree structure supplies nesting and perching habitat that flowering strips alone cannot provide.",
            "Deep roots retrieve nutrients below the crop rooting zone and cycle them to the surface as litter.",
        ],
        "watch_outs": [
            "Avoid dense, evergreen or shallow-rooted species in fields — they compete for water in exactly the season the crop needs it.",
            "Protection from browsing in years 1-3 determines survival more than planting density does.",
        ],
        "first_actions": [
            "Count existing stumps and rootstock per hectare — regeneration is far cheaper than planting where they exist.",
            "Mark a 20 m x 20 m grid for target stems and protect natural regeneration on those points.",
            "Confirm species choice against local rainfall and any tree tenure rules before planting.",
        ],
        "tags": ["structure", "carbon", "water", "yield"],
        "score": lambda f, c: (
            2.2
            + (1.2 if f["water_limited"] else 0)
            + (0.9 if f["low_tree_cover"] else 0.3)
            + (0.8 if f["cropland"] else 0)
            + (0.6 if f["monoculture"] else 0)
            + (0.5 if f["erosion"] else 0)
            - (1.1 if f["forest"] else 0)
            - (2.5 if f["wetland"] else 0)
        ),
    },
    {
        "key": "water_harvesting",
        "title": "In-field water partitioning: contour bunds, tied ridges and mulch",
        "what": (
            "Re-partition rainfall before it leaves the field: contour bunds or half-moon micro-catchments on slopes "
            "above 1%, tied ridges within the crop, and 3-5 t/ha of surface mulch. Target the runoff-producing "
            "portion of the field first, identified after the first heavy rain of the season."
        ),
        "why": (
            "In semi-arid rainfed systems only 15-30% of rainfall is actually transpired by the crop; the rest is "
            "lost to soil evaporation, runoff and deep drainage. Structures plus mulch can raise water productivity "
            "50-100% with no change in rainfall at all. This reframes the problem: the yield gap in these systems is "
            "a water-partitioning problem, not a rainfall problem, which is why this outranks drought-tolerant "
            "varieties as a first move."
        ),
        "metrics": [
            _m("water_productivity", "increase", "+50-100% per mm of rainfall", "short"),
            _m("infiltration", "increase", "large gain on crusted surfaces", "short"),
            _m("erosion", "decrease", "runoff interception at source", "short"),
            _m("yield_stability", "increase", "narrows the 50-80% rainfed yield gap", "medium"),
        ],
        "horizon": "short",
        "evidence": ["ROCKSTROM-2010-AGWATER", "IPCC-SRCCL-2019", "UNCCD-GLO2-2022"],
        "interactions": [
            "Infiltrated water supports the cover crop that builds carbon, which in turn holds more of the next season's rain.",
            "Reduced runoff lowers sediment and nutrient delivery to downstream water bodies.",
            "Longer soil moisture duration extends the activity window for earthworms and microbial turnover.",
        ],
        "watch_outs": [
            "Structures on the wrong contour concentrate rather than spread flow — survey with a line level before building.",
            "In high-rainfall years tied ridges can waterlog heavy clays; leave overflow points.",
        ],
        "first_actions": [
            "Walk the field after the first heavy rain and mark where water leaves it.",
            "Survey contours with an A-frame or line level; stake bund lines.",
            "Secure a mulch source (crop residue, pruning material) before the dry season, not during it.",
        ],
        "tags": ["water", "short-term"],
        "score": lambda f, c: (
            1.9
            + (1.6 if f["water_limited"] else 0)
            + (0.6 if f["water_erratic"] else 0)
            + (0.7 if f["erosion"] else 0)
            + (0.4 if f["cropland"] or f["grazing"] else 0)
            - (2.2 if f["wetland"] or f["water_excess"] else 0)
        ),
    },
    {
        "key": "functional_rotation",
        "title": "Rotation redesign by functional distance, not crop count",
        "what": (
            "Replace the continuous single-crop sequence with at least two functionally distinct phases — a legume "
            "and a non-host brassica or grass — before the main crop returns. Choose the break crops by pathogen "
            "host status and rooting depth rather than by market familiarity."
        ),
        "why": (
            "Continuous monoculture accumulates host-specific pathogens and nematodes, creating negative plant-soil "
            "feedback that suppresses yield independently of nutrient supply — which is why fertiliser increases stop "
            "working. Breaking the cycle with functionally distinct crops measurably reduces inoculum and restores "
            "positive feedback. Diversification across 5,160 studies raised associated biodiversity by 24%, pest "
            "control by 19% and water regulation by 51% while maintaining or increasing yield in most cases."
        ),
        "metrics": [
            _m("disease_pressure", "decrease", "measurable inoculum reduction over 2 seasons", "medium"),
            _m("species_richness", "increase", "+24% associated biodiversity (meta-analytic mean)", "medium"),
            _m("pest_control", "increase", "+19%", "medium"),
            _m("yield_stability", "increase", "maintained or improved in 63% of studies", "medium"),
        ],
        "horizon": "medium",
        "evidence": ["VANDERPUTTEN-2013-ROTATION", "TAMBURINI-2020-SCIADV", "BEILLOUIN-2021-GCB"],
        "interactions": [
            "The legume phase supplies nitrogen, which reduces fertiliser cost and nitrate export at the same time.",
            "Rooting-depth contrast between phases opens biopores that improve infiltration.",
            "Flowering break crops supply forage in the gap between main-crop bloom periods.",
        ],
        "watch_outs": [
            "A rotation of two cereals is taxonomic, not functional, diversity — pathogen carryover continues.",
            "Check market or fodder demand for the break crop before committing area.",
        ],
        "first_actions": [
            "List the main pathogens and nematodes recorded on the current crop; choose non-hosts.",
            "Trial the break sequence on two strips before whole-field adoption.",
        ],
        "tags": ["diversification", "yield", "soil"],
        "score": lambda f, c: (
            1.8
            + (1.5 if f["monoculture"] else 0)
            + (0.8 if f["yield_decline"] else 0)
            + (0.6 if f["pest_outbreak"] else 0)
            + (0.5 if f["cropland"] else -1.8)
        ),
    },
    {
        "key": "infield_habitat",
        "title": "Two-scale habitat design: in-field predator banks plus landscape forage patches",
        "what": (
            "Build raised tussock-grass beetle banks through the field interior every 100-200 m, and separately "
            "establish flowering patches sized so that no point in the production area is more than 150-500 m from "
            "forage. Use a mix of at least 15 flowering species with overlapping early, mid and late bloom."
        ),
        "why": (
            "Pollinators and natural enemies respond to different scales: pollinators track landscape-scale "
            "semi-natural habitat while natural enemies track local field-scale structure. A perimeter hedge alone "
            "therefore fixes neither in a large block — predators cannot reach the centre early in the season, and "
            "forage sits outside solitary-bee range. Beetle banks hold over 1,000 overwintering predators per square "
            "metre, and taking 3-8% of the least productive area out of production has raised whole-field yield by "
            "up to 35% for pollinator-dependent crops within five years."
        ),
        "metrics": [
            _m("natural_enemy_abundance", "increase", ">1,000 overwintering predators/m² in banks", "medium"),
            _m("pollinator_abundance", "increase", "progressive gain over 3-4 years", "medium"),
            _m("pest_control", "increase", "+19% service delivery", "medium"),
            _m("yield", "increase", "up to +35% whole-field for pollinator-dependent crops", "long"),
        ],
        "horizon": "medium",
        "evidence": ["SHACKELFORD-2013-BIOREV", "HOLLAND-2016-PESTMGMT", "PYWELL-2015-PRSB", "BLAAUW-ISAACS-2014", "RICKETTS-2008-ECOLLETT"],
        "interactions": [
            "Habitat only converts to service if chemical load falls — pair with the input-reduction step or expect muted response.",
            "Bank vegetation also intercepts runoff, linking the pest-control measure to erosion and water quality.",
            "Gains are largest in simplified landscapes holding 1-20% semi-natural cover; near-zero-cover landscapes need a source population first.",
        ],
        "watch_outs": [
            "Single-species 'wildflower' mixes support one guild and one bloom window — species count and phenology spread matter more than area.",
            "Mowing or spraying banks during the overwintering period cancels the benefit.",
        ],
        "first_actions": [
            "Measure the longest distance from any field point to existing habitat; if over 500 m, place the first patch there.",
            "Sow banks with tussock grasses in autumn; establish flowering strips on the least productive 3-5%.",
        ],
        "tags": ["habitat", "pollinators", "pest control"],
        "score": lambda f, c: (
            1.7
            + (1.3 if f["simplified_landscape"] else 0.4)
            + (1.0 if f["pollinator_concern"] else 0)
            + (0.7 if f["pest_outbreak"] else 0)
            + (0.5 if (c.get("area_ha") or 0) > 10 else 0)
            - (1.2 if f["cleared_landscape"] else 0)
            - (1.8 if f["wetland"] else 0)
        ),
    },
    {
        "key": "input_reduction",
        "title": "Threshold-based pesticide reduction before any habitat spend",
        "what": (
            "Replace calendar spraying and prophylactic seed treatments with monitored economic thresholds: weekly "
            "scouting, action only above threshold, selective products applied outside bloom, and a no-spray buffer "
            "around habitat features."
        ),
        "why": (
            "Insect biomass is falling about 2.5% per year, with chemical load the second-ranked driver after habitat "
            "loss — but it is the fastest-reversing one, since populations rebound within 1-3 generations once "
            "exposure stops. Farmer field school programmes have cut applications 35-92% with maintained yields. "
            "Sequencing matters: habitat built while exposure continues becomes an ecological trap, drawing "
            "invertebrates into treated fields."
        ),
        "metrics": [
            _m("pesticide_risk", "decrease", "-35-92% applications with maintained yield", "short"),
            _m("natural_enemy_abundance", "increase", "recovery within 1-3 generations", "short"),
            _m("pollinator_abundance", "increase", "compounds with habitat measures", "medium"),
            _m("net_benefit", "increase", "direct input cost saving from season one", "short"),
        ],
        "horizon": "short",
        "evidence": ["SANCHEZBAYO-2019-BIOCON", "FAO-IPM-2021", "DAINESE-2019-SCIADV", "CBD-GBF-2022"],
        "interactions": [
            "Recovered natural enemies substitute for the removed applications, so the two effects reinforce rather than trade off.",
            "Lower chemical load also reduces residue transport to adjacent water and soil fauna.",
        ],
        "watch_outs": [
            "Dropping a product without scouting in place transfers risk to yield — build the monitoring routine first.",
            "Neighbouring spray drift can mask on-farm gains; buffer edges facing treated land.",
        ],
        "first_actions": [
            "Set weekly scouting on a fixed transect with recorded counts and published thresholds.",
            "Stop prophylactic seed treatment on the next order and compare two blocks.",
        ],
        "tags": ["pollution", "pollinators", "quick win"],
        "score": lambda f, c: (
            1.5
            + (1.5 if f["high_chemical"] else 0)
            + (1.0 if f["pollinator_concern"] else 0)
            + (0.5 if f["pest_outbreak"] else 0)
            + (0.3 if f["cropland"] else 0)
        ),
    },
    {
        "key": "riparian_buffer",
        "title": "Placed riparian buffer sized to the flow path, not to the map",
        "what": (
            "Establish a 30-50 m vegetated buffer of mixed woody and herbaceous species along watercourses and "
            "drains, positioned where subsurface flow actually intersects the root zone. Identify the flow "
            "convergence points first; a placed 30 m buffer outperforms a uniform 10 m strip."
        ),
        "why": (
            "Riparian buffers remove a median 60-70% of incoming nitrate, rising above 85% at widths over 50 m, but "
            "they fail where groundwater bypasses the rooting depth — placement dominates width. Woody buffers add "
            "shading, bank stability and habitat value that herbaceous buffers do not. Because catchment loading "
            "resets in-channel work, this treats the driver rather than the symptom."
        ),
        "metrics": [
            _m("nitrate_removal", "increase", "60-70% median removal; >85% above 50 m", "medium"),
            _m("water_quality", "increase", "lower nutrient and sediment load", "medium"),
            _m("habitat_connectivity", "increase", "linear corridor along the drainage network", "long"),
            _m("freshwater_species_richness", "increase", "follows water quality with a lag", "long"),
        ],
        "horizon": "medium",
        "evidence": ["MAYER-2007-JEQ", "VOROSMARTY-2010-NATURE", "PALMER-2014-SCIENCE", "UNEP-NITROGEN-2019"],
        "interactions": [
            "Buffer benefit is capped by upstream input rates — pair with nitrogen efficiency or it plateaus.",
            "Riparian corridors double as dispersal routes, connecting otherwise isolated habitat patches.",
        ],
        "watch_outs": [
            "Tile drains and deep groundwater can bypass the buffer entirely; check drainage layout before committing area.",
            "Grazing access destroys bank vegetation faster than it establishes — fence before planting.",
        ],
        "first_actions": [
            "Map drains and flow convergence points after a heavy rain event.",
            "Fence the first 500 m of the highest-load reach and plant a mixed woody-herbaceous strip.",
        ],
        "tags": ["water quality", "connectivity"],
        "score": lambda f, c: (
            1.4
            + (1.5 if f["wetland"] else 0)
            + (1.2 if f["external_pollution"] or f["eutrophic"] else 0)
            + (1.0 if f["fish_amphibian"] else 0)
            + (0.6 if f["high_nitrogen"] else 0)
        ),
    },
    {
        "key": "wetland_hydrology",
        "title": "Restore flooding depth and duration before touching vegetation",
        "what": (
            "Re-establish the seasonal hydrograph — depth, timing and duration of inundation — by blocking or "
            "regulating drainage, restoring inflow connections and removing barriers, then let vegetation respond "
            "before deciding on any planting."
        ),
        "why": (
            "Hydrology is the primary control on whether wetland vegetation and amphibian assemblages recover; "
            "planting into the wrong water regime fails. Restored wetlands still average 26% lower biological "
            "structure and 23% lower biogeochemical function than reference sites even decades later, and recovery is "
            "fastest in large wetlands connected to rivers — so connection and size should be prioritised over "
            "cosmetic planting."
        ),
        "metrics": [
            _m("hydrological_function", "increase", "seasonal regime re-established", "medium"),
            _m("species_richness", "increase", "amphibians and waterbirds respond in 2-5 years", "long"),
            _m("carbon_sequestration", "increase", "rewetted soils switch from source to sink", "long"),
            _m("water_quality", "increase", "retention of sediment and nutrients", "medium"),
        ],
        "horizon": "long",
        "evidence": ["RAMSAR-GWO-2018", "MORENOMATEOS-2012-PLOSBIO", "PALMER-2014-SCIENCE", "IUCN-NBS-STANDARD-2020"],
        "interactions": [
            "Rewetting without cutting external nutrient load produces algal dominance rather than diverse macrophytes.",
            "Hydrological connection to a river drives both recovery speed and fish access.",
        ],
        "watch_outs": [
            "Rewetting can mobilise stored sulphate or phosphorus in previously drained soils — test before large-scale rewetting.",
            "Expect a multi-decadal trajectory; set 5-year milestones rather than pass/fail targets.",
        ],
        "first_actions": [
            "Install a simple staff gauge and record water depth weekly for one full season.",
            "Map and prioritise the drains that most reduce inundation duration.",
        ],
        "tags": ["wetland", "hydrology"],
        "score": lambda f, c: (1.2 + (3.0 if f["wetland"] else -2.5) + (0.6 if f["fish_amphibian"] or f["birds"] else 0)),
    },
    {
        "key": "natural_regeneration",
        "title": "Assisted natural regeneration first, enrichment planting only for the gaps",
        "what": (
            "Where remnant forest is within seed-dispersal distance and soil is not compacted, protect the site from "
            "fire and grazing and let it regenerate; add enrichment planting only for late-successional and "
            "dispersal-limited species that will not arrive on their own."
        ),
        "why": (
            "Natural regeneration outperformed active planting for biodiversity by 34-56% and for vegetation "
            "structure recovery, at far lower cost, wherever seed sources remained nearby. Second-growth tropical "
            "forest accumulates roughly 3 t C/ha/yr in its first 20 years, but species composition recovers far more "
            "slowly than biomass — which is exactly why targeted enrichment beats blanket planting."
        ),
        "metrics": [
            _m("species_richness", "increase", "+34-56% vs active planting where seed sources remain", "long"),
            _m("carbon_sequestration", "increase", "≈3 t C/ha/yr in first 20 years", "long"),
            _m("forest_cover", "increase", "structural recovery within 15-20 years", "long"),
            _m("habitat_connectivity", "increase", "depends on patch placement", "long"),
        ],
        "horizon": "long",
        "evidence": ["CROUZEILLES-2016-NATCOMM", "CHAZDON-2016-SCIADV", "FAO-FRA-2020", "GRISCOM-2017-PNAS"],
        "interactions": [
            "Regrowth patches raise matrix permeability, improving movement for species dependent on fragmented habitat.",
            "Canopy closure suppresses aggressive grasses that otherwise lock the site in an arrested state.",
        ],
        "watch_outs": [
            "Where aggressive grasses dominate or soil is compacted, unaided regeneration stalls — that is the case for active planting.",
            "Do not afforest species-rich natural grassland; it is a net biodiversity loss even when above-ground carbon rises.",
        ],
        "first_actions": [
            "Measure distance to the nearest remnant forest patch and count natural seedlings per 100 m².",
            "Establish fire breaks and grazing exclusion before any planting budget is spent.",
        ],
        "tags": ["forest", "carbon", "restoration"],
        "score": lambda f, c: (1.2 + (2.4 if f["forest"] else -2.0) + (0.5 if f["fragmentation"] else 0)),
    },
    {
        "key": "planned_grazing",
        "title": "Planned rotational grazing with enforced rest periods",
        "what": (
            "Split the range into paddocks and move stock on a recovery-based schedule — graze short, rest long, "
            "with rest keyed to basal cover recovery rather than the calendar. Retain standing residual cover through "
            "the dry season."
        ),
        "why": (
            "Grazing effects on grassland carbon depend on grass functional type and rainfall: intensity raised SOC "
            "6-7% on C4-dominated grassland but cut it up to 18% on C3-dominated grassland. In drier sites moderate "
            "stocking with planned rest consistently outperformed both continuous heavy grazing and full exclusion, "
            "because periodic defoliation stimulates root turnover while rest restores basal cover. Semi-natural "
            "grassland also stores most of its carbon below ground, making it more drought- and fire-resilient than "
            "afforestation in dry regions."
        ),
        "metrics": [
            _m("soil_organic_carbon", "increase", "+6-7% on C4 systems under planned rest", "long"),
            _m("vegetation_cover", "increase", "basal cover recovery within 2 seasons", "medium"),
            _m("species_richness", "increase", "grassland forbs and ground-nesting birds respond", "medium"),
            _m("infiltration", "increase", "reduced capping and hoof compaction", "medium"),
        ],
        "horizon": "medium",
        "evidence": ["MCSHERRY-RITCHIE-2013", "BENGTSSON-2019-ECOSPHERE", "SMITH-2019-GCB"],
        "interactions": [
            "Higher basal cover increases infiltration, which extends the growing window that the rest period depends on.",
            "Retained residual cover provides nesting structure for ground-nesting birds and invertebrates.",
        ],
        "watch_outs": [
            "Identify whether the sward is C3- or C4-dominated first; the carbon response reverses between them.",
            "Full exclusion is not the safe default — it can reduce both diversity and carbon in grazing-adapted systems.",
        ],
        "first_actions": [
            "Record basal cover and species composition on three fixed transects before changing the schedule.",
            "Set paddock moves on a cover trigger, not a date.",
        ],
        "tags": ["grassland", "grazing", "carbon"],
        "score": lambda f, c: (1.1 + (2.6 if f["grazing"] else -2.2) + (0.4 if f["water_limited"] else 0)),
    },
    {
        "key": "ph_correction",
        "title": "Correct the chemical constraint before investing in biology",
        "what": (
            "On acidic soils (pH below 5.5) apply 1-3 t/ha of lime based on a buffer test; on sodic soils apply "
            "gypsum with a deep-rooted salt-tolerant cover. In both cases add organic matter to buffer the change."
        ),
        "why": (
            "Soil pH is the strongest single predictor of bacterial community composition, with diversity peaking "
            "between pH 6.0 and 7.5 and falling sharply below 5.5 where aluminium toxicity also limits roots. Liming "
            "raises pH roughly 0.5-1.0 unit over 1-2 seasons and restores phosphorus availability. Cover crops and "
            "habitat measures underperform while the chemical constraint binds, so ordering matters."
        ),
        "metrics": [
            _m("soil_ph", "stabilise", "+0.5-1.0 unit over 1-2 seasons", "short"),
            _m("microbial_diversity", "increase", "community shift toward pH optimum", "medium"),
            _m("yield", "increase", "phosphorus availability restored", "medium"),
        ],
        "horizon": "short",
        "evidence": ["FAO-SOILPH-2022", "FAO-ITPS-SOILBIO-2020", "BARDGETT-2014-NATURE"],
        "interactions": [
            "Higher pH increases phosphorus availability, which also raises legume nodulation in the cover-crop step.",
            "Organic matter addition buffers pH in both directions, linking this to the carbon measure.",
        ],
        "watch_outs": [
            "Over-liming locks up micronutrients — dose from a buffer test, not from the pH value alone.",
            "Gypsum without drainage moves salts sideways rather than out.",
        ],
        "first_actions": [
            "Run a lab pH and buffer test on composited samples before purchasing any amendment.",
        ],
        "tags": ["soil chemistry"],
        "score": lambda f, c: (0.6 + (2.6 if f["acidic"] else 0) + (1.4 if f["alkaline"] else 0) + (1.2 if f["saline"] else 0)),
    },
    {
        "key": "biodrainage",
        "title": "Biodrainage strips to pull down a shallow saline water table",
        "what": (
            "Plant deep-rooted perennial strips (lucerne, Prosopis, Atriplex, Leptochloa) across 5-10% of the area, "
            "aligned across the direction of the shallow water table, and use them for fodder and windbreak."
        ),
        "why": (
            "Where the water table sits within 2 m of the surface in arid irrigated systems, capillary rise "
            "concentrates salts in the root zone, and leaching alone displaces rather than solves the problem where "
            "drainage is poor. Deep-rooted perennials lower water tables 0.3-1.0 m per season while supplying fodder "
            "and habitat structure — a case where the biodiversity measure and the salinity fix are the same action."
        ),
        "metrics": [
            _m("salinity", "decrease", "root-zone EC falls as water table drops 0.3-1.0 m/season", "medium"),
            _m("vegetation_cover", "increase", "perennial strips establish permanent cover", "medium"),
            _m("habitat_diversity", "increase", "structure and dry-season forage", "long"),
        ],
        "horizon": "medium",
        "evidence": ["GILBERT-BUNDY-SALINITY", "FAO-SOILPH-2022", "IPCC-SRCCL-2019"],
        "interactions": [
            "Lower water table reduces salt accumulation, which is what allows cover crops to establish at all.",
            "Perennial strips double as windbreaks, cutting evaporative demand across the adjoining field.",
        ],
        "watch_outs": [
            "Some biodrainage species are invasive outside their range — check status before planting Prosopis.",
            "Strips consume water; on non-saline sites they compete with the crop for it.",
        ],
        "first_actions": [
            "Install a shallow observation well and record water-table depth monthly.",
            "Take an EC profile at 0-30 and 30-60 cm.",
        ],
        "tags": ["salinity", "water"],
        "score": lambda f, c: (0.4 + (3.0 if f["saline"] else -2.5) + (0.6 if f["irrigated"] else 0)),
    },
    {
        "key": "nitrogen_efficiency",
        "title": "Nitrogen efficiency: split application, placement and legume substitution",
        "what": (
            "Split nitrogen into growth-stage-matched doses, place it in the root zone instead of broadcasting, and "
            "substitute 30-50% of the rate with the legume phase and manure from integrated livestock."
        ),
        "why": (
            "Only about 20% of applied reactive nitrogen ends up in food; the remainder drives eutrophication and "
            "biodiversity loss in nitrogen-sensitive habitats, which shift toward a few nitrophilous species above "
            "critical loads of 10-20 kg N/ha/yr. Integrated crop-livestock systems cut fertiliser purchases 30-50% "
            "while raising soil organic matter — the rare case where the cost saving and the biodiversity gain come "
            "from the same change."
        ),
        "metrics": [
            _m("nitrate_removal", "increase", "lower leaching load at source", "short"),
            _m("net_benefit", "increase", "30-50% lower fertiliser purchase", "short"),
            _m("species_richness", "increase", "relief for nitrogen-sensitive margin flora", "medium"),
            _m("water_quality", "increase", "reduced downstream loading", "medium"),
        ],
        "horizon": "short",
        "evidence": ["UNEP-NITROGEN-2019", "GARRETT-2017-AGSYS", "BOMMARCO-2013-TREE", "TEEB-AGRIFOOD-2018"],
        "interactions": [
            "Cuts the load the riparian buffer has to intercept, so the two compound instead of duplicating.",
            "Lower nitrogen favours mycorrhizal association, which supports the soil-carbon pathway.",
        ],
        "watch_outs": [
            "Cutting rate without placement or timing changes usually costs yield — change the method first, the rate second.",
        ],
        "first_actions": [
            "Record current kg N/ha and split it across at least two growth stages this season.",
            "Trial a 20% rate reduction on one block with placement, and compare.",
        ],
        "tags": ["inputs", "water quality", "economics"],
        "score": lambda f, c: (0.8 + (1.6 if f["high_nitrogen"] else 0) + (1.0 if f["external_pollution"] or f["eutrophic"] else 0) + (0.4 if f["cropland"] else 0)),
    },
    {
        "key": "connectivity",
        "title": "Connectivity: stepping stones sized to the dispersal distance of your indicator taxa",
        "what": (
            "Place habitat patches so that no gap exceeds 1 km, target at least 20% semi-natural cover across the "
            "management unit, and make the productive matrix permeable — flowering margins, untilled strips, "
            "unsprayed edges — rather than relying on a single reserved block."
        ),
        "why": (
            "70% of remaining forest sits within 1 km of an edge, and experimental fragmentation reduced species "
            "persistence and nutrient retention by 13-75%, with effects growing over time. Connected patches hold "
            "roughly 20% more species than isolated patches of the same area. Below about 20% natural cover species "
            "loss accelerates non-linearly, so the target is a threshold rather than a preference — and matrix "
            "permeability matters as much as the patches themselves."
        ),
        "metrics": [
            _m("habitat_connectivity", "increase", "+~20% species richness in connected vs isolated patches", "long"),
            _m("species_richness", "increase", "compounds over 5-10 years", "long"),
            _m("pollinator_abundance", "increase", "gaps kept within solitary-bee foraging range", "medium"),
        ],
        "horizon": "long",
        "evidence": ["HADDAD-2015-SCIADV", "KREMEN-MERENLENDER-2018", "TSCHARNTKE-2012-BIOCON", "NEWBOLD-2015-NATURE"],
        "interactions": [
            "Connectivity multiplies the return on local habitat work; in isolation the same strips saturate quickly.",
            "In landscapes under 1% natural cover there is no source population, so patch creation must come with reintroduction or upstream source protection.",
        ],
        "watch_outs": [
            "Corridors that funnel movement through sprayed or heavily grazed land act as traps.",
            "Measure gain against a baseline patch map, or it is impossible to demonstrate.",
        ],
        "first_actions": [
            "Map existing patches (10 m land-cover data works) and measure the largest gap.",
            "Site the first new patch to cut that gap in half.",
        ],
        "tags": ["landscape", "connectivity"],
        "score": lambda f, c: (1.0 + (1.6 if f["fragmentation"] else 0) + (1.0 if f["simplified_landscape"] else 0) + (0.6 if f["forest"] else 0)),
    },
    {
        "key": "monitoring",
        "title": "Baseline and monitoring loop, set before the first intervention",
        "what": (
            "Fix five georeferenced monitoring points. Record SOC and bulk density annually after harvest; wild bee "
            "and ground beetle counts on a fixed transect three times per season; earthworm counts in two 20 cm "
            "cubes per point in spring; vegetation cover photographs from fixed markers each season."
        ),
        "why": (
            "The IUCN Global Standard treats an adaptive management loop with measurable indicators as a requirement, "
            "not an optional extra, and land-degradation-neutrality accounting requires land cover, productivity and "
            "SOC to be tracked together, since improvement in one while another declines is not neutrality. "
            "Consistency of method and timing matters more than taxonomic completeness for detecting trend — five "
            "repeated points beat a one-off comprehensive survey."
        ),
        "metrics": [
            _m("soil_organic_carbon", "stabilise", "trend detectable after 2-3 annual samples", "medium"),
            _m("species_richness", "stabilise", "indicator-taxa trend over 3 seasons", "medium"),
            _m("earthworm_density", "stabilise", "target above 100/m² in temperate soils", "medium"),
        ],
        "horizon": "short",
        "evidence": ["IUCN-NBS-STANDARD-2020", "GEOBON-EBV-2013", "UNCCD-GLO2-2022", "ISRIC-SOILGRIDS-2021"],
        "interactions": [
            "Without a baseline, none of the projected metric changes above can be claimed or verified.",
            "The same dataset underpins carbon or biodiversity credit eligibility later.",
        ],
        "watch_outs": [
            "Changing method or timing between years destroys comparability more often than sampling error does.",
        ],
        "first_actions": [
            "Mark five points with GPS and a physical marker this month.",
            "Take the pre-intervention soil samples before any amendment is applied.",
        ],
        "tags": ["monitoring", "verification"],
        "score": lambda f, c: 1.25,
    },
]


# --------------------------------------------------------------------------- confidence
def _confidence(
    intervention: Dict[str, Any],
    ctx: Dict[str, Any],
    completeness: float,
    flags: Dict[str, bool],
    fit: float,
) -> Dict[str, Any]:
    """Confidence = evidence strength x site fit x how much we actually know about the site.

    It is deliberately not a fixed number per intervention: the same measure is
    high-confidence on a well-characterised site that matches the evidence base and
    only indicative where the key variables were assumed.
    """
    from ..knowledge import corpus as kb_corpus

    docs = [d for d in (kb_corpus.by_id(e) for e in intervention["evidence"]) if d]
    tier_weight = {"meta_analysis": 0.075, "peer_reviewed": 0.05, "institutional": 0.06}
    evidence_score = min(0.24, sum(tier_weight.get(d["tier"], 0.03) for d in docs))

    biome = ctx.get("biome")
    biome_match = any(biome in d["biomes"] for d in docs) if biome else False
    generic_only = bool(biome) and not biome_match

    # How well the site actually triggers this intervention (engine fit score).
    fit_component = max(-0.10, min(0.16, (fit - 2.6) * 0.055))

    # Which of the variables this intervention depends on were measured, not assumed.
    depends = {
        "soil": ["soil_organic_carbon", "soil_ph"],
        "water": ["rainfall_mm", "rainfall_pattern", "irrigation"],
        "habitat": ["natural_habitat_pct", "tree_cover_pct"],
        "inputs": ["pesticide_use", "fertiliser_kg_n_ha"],
    }
    needed: List[str] = []
    for tag in intervention["tags"]:
        for group, fields in depends.items():
            if group in tag or tag in group:
                needed.extend(fields)
    needed = needed or ["soil_organic_carbon", "rainfall_pattern"]
    measured = sum(1 for f in needed if ctx.get(f) not in (None, "", [], {})) / len(needed)

    value = 0.34 + evidence_score + 0.14 * completeness + 0.14 * measured + fit_component
    value += 0.05 if biome_match else 0.0
    value -= 0.04 if generic_only else 0.0
    value = round(max(0.35, min(0.93, value)), 2)

    label = "high" if value >= 0.78 else "moderate" if value >= 0.62 else "indicative"
    metas = sum(1 for d in docs if d["tier"] == "meta_analysis")
    insts = sum(1 for d in docs if d["tier"] == "institutional")
    basis = (
        f"{len(docs)} sources ({metas} meta-analyses, {insts} institutional); "
        f"{int(measured * 100)}% of the variables this depends on were measured rather than assumed; "
        f"site profile {int(completeness * 100)}% complete; "
        + ("evidence includes biome-matched studies" if biome_match else "evidence generalised across biomes")
    )
    return {"confidence": value, "confidence_label": label, "confidence_basis": basis}

def _constraint_adjustment(item: Dict[str, Any], ctx: Dict[str, Any]) -> float:
    """
    Adjust ecological ranking according to explicit user constraints.

    Important:
    - This does not replace ecological suitability.
    - It only changes prioritisation when the user explicitly states a constraint.
    """

    adjustment = 0.0

    lease = _num(ctx, "lease_years_remaining")
    budget = str(ctx.get("budget_constraint") or "").lower()
    no_trees = bool(ctx.get("tree_planting_constraint"))

    title = str(item.get("title", "")).lower()
    key = str(item.get("key", "")).lower()
    horizon = str(item.get("horizon", "")).lower()
    tags = {str(t).lower() for t in (item.get("tags") or [])}

    # ------------------------------------------------------------------
    # Lease constraint
    # ------------------------------------------------------------------
    if lease is not None:
        # Long-horizon interventions provide less practical value when
        # the user will leave the land before benefits can mature.
        if lease <= 2:
            if horizon == "long":
                adjustment -= 4.0
            elif horizon == "medium":
                adjustment -= 0.8
            elif horizon == "short":
                adjustment += 0.8

            # Explicitly penalise tree/agroforestry interventions.
            if (
                "tree" in title
                or "agroforestry" in title
                or "tree" in key
                or "agroforestry" in key
            ):
                adjustment -= 5.0

        elif lease <= 3:
            if horizon == "long":
                adjustment -= 2.0
            elif horizon == "short":
                adjustment += 0.4

    # ------------------------------------------------------------------
    # Explicit inability to plant trees
    # ------------------------------------------------------------------
    if no_trees:
        if (
            "tree" in title
            or "agroforestry" in title
            or "tree" in key
            or "agroforestry" in key
        ):
            adjustment -= 8.0

    # ------------------------------------------------------------------
    # Budget constraint
    # ------------------------------------------------------------------
    if budget == "low":
        # Prefer interventions that can start with relatively simple,
        # low-capital management changes.
        low_cost_tags = {
            "low-cost",
            "low cost",
            "management",
            "rotation",
            "cover crop",
            "residue",
            "monitoring",
            "water management",
        }

        if tags.intersection(low_cost_tags):
            adjustment += 1.5

        expensive_tags = {
            "infrastructure",
            "construction",
            "establishment",
            "capital",
        }

        if tags.intersection(expensive_tags):
            adjustment -= 1.5

        # Additional conservative penalty for long-horizon interventions
        # under a low-budget constraint.
        if horizon == "long":
            adjustment -= 1.0

    return adjustment
# --------------------------------------------------------------------------- main entry
def recommend(ctx: Context, completeness: float, limit: int = 5) -> Dict[str, Any]:
    diag = diagnose(ctx)
    flags = diag["flags"]

    scored = []
    for item in INTERVENTIONS:
        try:
           ecological_score = float(item["score"](flags, ctx))
        except Exception:
            ecological_score = 0.0

        constraint_score = _constraint_adjustment(item, ctx)
        final_score = ecological_score + constraint_score

        scored.append((final_score, item))
    scored.sort(key=lambda pair: -pair[0])

    # Keep only interventions the site actually calls for, but never return fewer
    # than three — a plan with one line is not a plan.
    strong = [pair for pair in scored if pair[0] >= 1.9][:limit]
    if len(strong) < 3:
        strong = scored[:3]
    chosen = strong

    recommendations: List[Dict[str, Any]] = []

    for rank, (score, item) in enumerate(chosen, start=1):
        conf = _confidence(item, ctx, completeness, flags, score)

        # Explain how explicit user constraints affected prioritisation.
        constraint_notes = []

        lease = _num(ctx, "lease_years_remaining")
        budget = str(ctx.get("budget_constraint") or "").lower()
        no_trees = bool(ctx.get("tree_planting_constraint"))

        if lease is not None and lease <= 2:
            constraint_notes.append(
                f"Prioritised for a {lease:g}-year remaining lease."
            )

        if budget == "low":
            constraint_notes.append(
                "Prioritised because you specified a low budget."
            )

        if no_trees:
            constraint_notes.append(
                "Tree-based interventions were deprioritised because tree planting is not feasible."
            )

        recommendations.append(
            {
                "rank": rank,
                "title": item["title"],
                "what_to_do": item["what"],
                "why_it_works": item["why"],
                "metrics": item["metrics"],
                "time_horizon": item["horizon"],
                "horizon_detail": HORIZON_DETAIL[item["horizon"]],
                "evidence_ids": item["evidence"],
                "interactions": item["interactions"],
                "watch_outs": item["watch_outs"],
                "first_actions": item["first_actions"],
                "tags": item["tags"],
                "constraint_notes": constraint_notes,
                "_fit": round(score, 2),
                **conf,
            }
        )

    return {
        "diagnosis": diag,
        "recommendations": recommendations,
        "linkages": diag["couplings"],
        "projection": project_metrics(ctx, recommendations),
        "monitoring": monitoring_plan(ctx, recommendations),
    }


# --------------------------------------------------------------------------- projections
def project_metrics(ctx: Context, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Quantified trajectory for the metrics the selected bundle actually moves."""
    keys = {m["metric"] for r in recommendations for m in r["metrics"]}
    out: List[Dict[str, Any]] = []

    soc = _num(ctx, "soil_organic_carbon")
    if "soil_organic_carbon" in keys:
        base = soc if soc is not None else 0.6
        out.append(
            {
                "metric": "soil_organic_carbon",
                "label": "Soil organic carbon (%)",
                "unit": "%",
                "baseline": round(base, 2),
                "year_1": round(base * 1.06, 2),
                "year_3": round(base * 1.20, 2),
                "year_5": round(base * 1.32, 2),
                "measured": soc is not None,
                "basis": "Cover crops + agroforestry: ~0.3 t C/ha/yr, 15-25% relative gain in low-carbon soils (Poeplau & Don 2015; Kuyah et al. 2019).",
            }
        )
        out.append(
            {
                "metric": "water_holding_capacity",
                "label": "Plant-available water (mm/m)",
                "unit": "mm per m",
                "baseline": round(base * 1.72 * 17, 1),
                "year_1": round(base * 1.06 * 1.72 * 17, 1),
                "year_3": round(base * 1.20 * 1.72 * 17, 1),
                "year_5": round(base * 1.32 * 1.72 * 17, 1),
                "measured": soc is not None,
                "basis": "≈17 mm of plant-available water per 1% soil organic matter per metre of profile (FAO 2017).",
            }
        )

    if {"pollinator_abundance", "natural_enemy_abundance", "pest_control"} & keys:
        natural = _num(ctx, "natural_habitat_pct")
        base = natural if natural is not None else 8.0
        index = min(100.0, base * 3.4 + 20)
        out.append(
            {
                "metric": "pollinator_abundance",
                "label": "Wild pollinator index (0-100)",
                "unit": "index",
                "baseline": round(index, 1),
                "year_1": round(min(100, index * 1.10), 1),
                "year_3": round(min(100, index * 1.38), 1),
                "year_5": round(min(100, index * 1.55), 1),
                "measured": natural is not None,
                "basis": "Flower plantings raise wild bee abundance progressively over 3-4 years; gains largest in simplified landscapes (Blaauw & Isaacs 2014; Tscharntke et al. 2012).",
            }
        )

    if "species_richness" in keys:
        natural = _num(ctx, "natural_habitat_pct") or 8.0
        base = 40 + natural * 1.2
        out.append(
            {
                "metric": "species_richness",
                "label": "Species richness vs reference (%)",
                "unit": "% of reference",
                "baseline": round(min(95, base), 1),
                "year_1": round(min(95, base * 1.04), 1),
                "year_3": round(min(95, base * 1.20), 1),
                "year_5": round(min(95, base * 1.30), 1),
                "measured": ctx.get("natural_habitat_pct") is not None,
                "basis": "Diversification raises associated biodiversity ~24%; connected patches hold ~20% more species than isolated ones (Tamburini et al. 2020; Haddad et al. 2015).",
            }
        )

    if {"water_productivity", "infiltration"} & keys:
        rain = _num(ctx, "rainfall_mm") or (450 if str(ctx.get("rainfall_pattern")) in {"low", "erratic"} else 900)
        productive = rain * 0.22
        out.append(
            {
                "metric": "water_productivity",
                "label": "Rainfall reaching the crop (mm)",
                "unit": "mm",
                "baseline": round(productive, 1),
                "year_1": round(productive * 1.25, 1),
                "year_3": round(productive * 1.6, 1),
                "year_5": round(productive * 1.8, 1),
                "measured": ctx.get("rainfall_mm") is not None,
                "basis": "Only 15-30% of rainfall is transpired in semi-arid rainfed systems; harvesting plus mulch raises water productivity 50-100% (Rockström et al. 2010).",
            }
        )

    if {"nitrate_removal", "water_quality"} & keys:
        out.append(
            {
                "metric": "nitrate_removal",
                "label": "Nitrate intercepted before watercourse (%)",
                "unit": "%",
                "baseline": 5.0,
                "year_1": 25.0,
                "year_3": 62.0,
                "year_5": 72.0,
                "measured": False,
                "basis": "Riparian buffers remove a median 60-70% of incoming nitrate once established (Mayer et al. 2007).",
            }
        )
    return out


def monitoring_plan(ctx: Context, recommendations: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    keys = {m["metric"] for r in recommendations for m in r["metrics"]}
    plan: List[Dict[str, str]] = [
        {
            "indicator": "Soil organic carbon and bulk density",
            "method": "Composite 0-15 cm and 15-30 cm samples from 5 fixed GPS points, same month each year",
            "frequency": "Annual, post-harvest",
            "target": "+0.1 percentage point within 3 years",
        }
    ]
    if {"pollinator_abundance", "species_richness", "pest_control"} & keys:
        plan.append(
            {
                "indicator": "Wild bees and ground beetles",
                "method": "Fixed 100 m transect walk (bees, 10 min, sunny) plus 5 pitfall traps for beetles",
                "frequency": "3 times per season, same weeks each year",
                "target": "Upward trend in abundance and morphospecies count by season 3",
            }
        )
    if {"microbial_diversity", "earthworm_density", "soil_organic_carbon"} & keys:
        plan.append(
            {
                "indicator": "Earthworm density",
                "method": "Two 20 x 20 x 20 cm soil cubes per point, hand-sorted",
                "frequency": "Annual, in moist spring conditions",
                "target": "Above 100 individuals/m² in temperate soils; rising trend in dry soils",
            }
        )
    if {"water_productivity", "infiltration"} & keys:
        plan.append(
            {
                "indicator": "Infiltration rate and soil moisture",
                "method": "Single-ring infiltrometer at 3 points; moisture at 20 cm before and 48 h after rain",
                "frequency": "Twice per season",
                "target": "Shorter ponding time and longer moisture retention year on year",
            }
        )
    if {"nitrate_removal", "water_quality"} & keys:
        plan.append(
            {
                "indicator": "Nitrate and turbidity at outflow",
                "method": "Field test strips or lab sample at the drain entering the watercourse",
                "frequency": "Monthly during the wet season",
                "target": "Downward trend in wet-season peaks",
            }
        )
    plan.append(
        {
            "indicator": "Habitat map and patch gaps",
            "method": "Annual land-cover snapshot (10 m satellite data) with largest inter-patch gap measured",
            "frequency": "Annual",
            "target": "Semi-natural cover trending toward 20%; no gap over 1 km",
        }
    )
    return plan


def headline(ctx: Context, diag: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
    flags = diag["flags"]
    bits: List[str] = []
    if flags["soc_critical"]:
        bits.append("a carbon-depleted soil that is also a water deficit")
    elif flags["soc_low"]:
        bits.append("a low soil carbon base")
    if flags["water_limited"]:
        bits.append("rainfall that is poorly partitioned rather than simply scarce")
    if flags["simplified_landscape"]:
        bits.append("a landscape below the 20% habitat threshold")
    if flags["high_chemical"]:
        bits.append("a chemical load suppressing invertebrate recovery")
    if flags["saline"]:
        bits.append("salinity driven by a shallow water table")
    if flags["wetland"]:
        bits.append("a wetland where hydrology, not planting, is the control")
    if not bits:
        bits.append("interacting soil, water and habitat constraints")
    lead = "; ".join(bits[:3])
    return f"Diagnosis: {lead}. {len(recommendations)} sequenced interventions follow."
