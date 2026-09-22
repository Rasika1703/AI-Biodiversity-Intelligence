"""
Recommendation / Reasoning Engine
-----------------------------------
This is where retrieved knowledge is turned into evidence-backed,
multi-metric recommendations. Every recommendation returned by this module
carries: what to do, why it works, which metrics it improves, a time
horizon, a confidence level, and a source citation -- as mandated by the
brief. It also explicitly links multiple environmental variables together
(soil <-> biodiversity, water <-> species survival, land use <->
fragmentation) rather than issuing single-variable advice.
"""
from typing import Dict, Any, List
from knowledge.retriever import KnowledgeRetriever

# Explicit cross-variable linkage map used to justify *why* recommendations
# span multiple metrics, satisfying the "Multi-Metric Reasoning" requirement.
VARIABLE_LINKS = {
    ("soil_organic_carbon", "biodiversity"):
        "Higher soil organic carbon supports greater microbial and invertebrate "
        "biomass, which underpins above-ground food webs and pollinator support.",
    ("water_availability", "species_survival"):
        "Water availability directly constrains species range and survival, "
        "especially for amphibians, insects, and riparian vegetation.",
    ("land_use", "habitat_fragmentation"):
        "Land-use intensity and homogeneity determine how fragmented habitat "
        "patches become, which in turn limits species movement and gene flow.",
    ("rainfall", "soil_moisture"):
        "Rainfall pattern governs baseline soil moisture, which constrains both "
        "crop viability and the soil microbial/faunal community.",
    ("pollution", "water_quality"):
        "Chemical input intensity directly determines downstream water quality "
        "and, through it, aquatic biodiversity.",
}


class RecommendationEngine:
    def __init__(self):
        self.retriever = KnowledgeRetriever()

    def _identify_active_links(self, variables: Dict[str, Any]) -> List[str]:
        """Report which cross-variable relationships are actually relevant
        given the variables the user has supplied."""
        active = []
        keys = set(variables.keys()) | {"biodiversity", "species_survival",
                                         "habitat_fragmentation", "water_quality",
                                         "soil_moisture"}
        for (a, b), explanation in VARIABLE_LINKS.items():
            if a in variables or a in keys:
                if b in keys:
                    active.append(explanation)
        return active

    def generate(self, variables: Dict[str, Any], free_text: str = "") -> Dict[str, Any]:
        docs = self.retriever.retrieve(variables, free_text=free_text, top_k=5)

        recommendations = []
        for doc in docs:
            recommendations.append({
                "recommendation": doc["intervention"],
                "why_it_works": doc["mechanism"],
                "supporting_finding": doc["finding"],
                "impacted_metrics": doc["impacted_metrics"],
                "quantitative_impact": doc["quantitative_impact"],
                "time_horizon": doc["time_horizon"],
                "confidence": doc["confidence"],
                "source": doc["source"],
                "retrieval_basis": "structured_match" if doc["id"] in
                    {d["id"] for d in self.retriever.structured_match(variables)}
                    else f"semantic_match (score={doc.get('_similarity_score', 'n/a')})",
            })

        multi_metric_reasoning = self._identify_active_links(variables)

        return {
            "input_variables": variables,
            "variables_considered": len(variables),
            "multi_metric_reasoning": multi_metric_reasoning,
            "recommendations": recommendations,
            "recommendation_count": len(recommendations),
        }

    def format_for_chat(self, result: Dict[str, Any]) -> str:
        """Render the structured result as a readable chat response."""
        if not result["recommendations"]:
            return ("I don't yet have enough matching knowledge-base evidence for this "
                    "exact combination of conditions. Could you share more detail "
                    "(soil pH, pollution levels, or crop type)?")

        lines = [
            f"Based on {result['variables_considered']} environmental variables you've "
            f"provided, here's my analysis:\n"
        ]

        if result["multi_metric_reasoning"]:
            lines.append("**Cross-variable relationships in play:**")
            for link in result["multi_metric_reasoning"][:3]:
                lines.append(f"- {link}")
            lines.append("")

        lines.append("**Recommendations:**\n")
        for i, rec in enumerate(result["recommendations"], 1):
            lines.append(f"**{i}. {rec['recommendation']}**")
            lines.append(f"   - Why it works: {rec['why_it_works']}")
            lines.append(f"   - Expected impact: {rec['quantitative_impact']}")
            lines.append(f"   - Metrics improved: {', '.join(rec['impacted_metrics'])}")
            lines.append(f"   - Time horizon: {rec['time_horizon']} | Confidence: {rec['confidence']}")
            lines.append(f"   - Source: {rec['source']}")
            lines.append("")

        return "\n".join(lines)
