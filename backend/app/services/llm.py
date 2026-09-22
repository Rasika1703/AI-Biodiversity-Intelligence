"""
LLM narration layer.

Important design decision: the LLM never invents the recommendations. The
reasoning engine selects and ranks them and the retrieval layer supplies the
evidence; the model is given both and asked only to write the analyst's narrative
that ties them together, with an explicit instruction not to add facts or figures
that are not in the supplied evidence. If no API key is set, a deterministic
narrative is composed from the same structures, so the product degrades in style
rather than in substance.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..config import settings

log = logging.getLogger("darukaa.llm")

SYSTEM_PROMPT = """You are the narrating voice of Darukaa.Earth, an AI environmental scientist for land managers, ecologists and restoration teams.

You are given:
- SITE CONTEXT: structured variables extracted from the conversation.
- DIAGNOSIS: the constraints the reasoning engine found binding and how they interact.
- SELECTED INTERVENTIONS: already ranked. Do not add, remove or reorder them.
- EVIDENCE: retrieved passages from a curated corpus. These are the only facts you may cite.

Write the analyst's narrative that goes above the structured recommendation cards.

Rules:
- 130-220 words, plain prose, no headings, no bullet lists, no markdown emphasis.
- Open with the causal chain: which variable is limiting, what it constrains next, and why that ordering matters here. Be specific to the numbers given.
- Refer to interventions by their short name and explain the sequence — what has to happen first for the next step to work.
- Cite sources inline in square brackets using the evidence ids exactly as given, e.g. [POEPLAU-DON-2015]. Cite at least three.
- Never state a figure that is not present in the EVIDENCE or SITE CONTEXT.
- If a variable was assumed rather than measured, say so once, briefly.
- No greetings, no offers to help further, no restating the user's message.
"""


def _client():
    try:
        import anthropic  # noqa: WPS433

        return anthropic.Anthropic(api_key=settings.anthropic_api_key)
    except Exception as exc:  # pragma: no cover
        log.warning("Anthropic SDK unavailable: %s", exc)
        return None


def _format_evidence(citations: List[Dict[str, Any]]) -> str:
    return "\n".join(
        f"[{c['id']}] {c['title']} — {c['source']} ({c['year']}). {c['snippet']}" for c in citations
    )


def _format_context(ctx: Dict[str, Any]) -> str:
    if not ctx:
        return "(no variables captured yet)"
    return "\n".join(f"- {k}: {v}" for k, v in ctx.items() if v not in (None, "", [], {}))


def narrate(
    ctx: Dict[str, Any],
    diagnosis: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
    citations: List[Dict[str, Any]],
    assumptions: List[str],
    history: List[Dict[str, str]],
) -> Dict[str, str]:
    """Return {'text': ..., 'generator': ...}."""
    fallback = _fallback_narrative(ctx, diagnosis, recommendations, citations, assumptions)
    if not settings.llm_enabled:
        return {"text": fallback, "generator": "reasoning-engine (no API key set)"}

    client = _client()
    if client is None:
        return {"text": fallback, "generator": "reasoning-engine (SDK unavailable)"}

    active_flags = [k for k, v in diagnosis["flags"].items() if v]
    interventions = "\n".join(
        f"{r['rank']}. {r['title']} — horizon {r['horizon_detail']}, confidence {r['confidence']} "
        f"({r['confidence_label']}), evidence {', '.join(r['evidence_ids'])}"
        for r in recommendations
    )
    couplings = "\n".join(
        f"- {c['source']} {c['relation']} {c['target']}: {c['explanation']}" for c in diagnosis["couplings"]
    )
    user_block = (
        f"SITE CONTEXT\n{_format_context(ctx)}\n\n"
        f"ASSUMPTIONS MADE\n{chr(10).join('- ' + a for a in assumptions) or '- none'}\n\n"
        f"DIAGNOSIS FLAGS\n{', '.join(active_flags) or 'none'}\n\n"
        f"VARIABLE COUPLINGS\n{couplings}\n\n"
        f"SELECTED INTERVENTIONS (fixed order)\n{interventions}\n\n"
        f"EVIDENCE\n{_format_evidence(citations)}"
    )

    messages = []
    for turn in history[-6:]:
        if turn["role"] in ("user", "assistant") and turn["content"].strip():
            messages.append({"role": turn["role"], "content": turn["content"][:1500]})
    messages.append({"role": "user", "content": user_block})

    try:
        response = client.messages.create(
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text").strip()
        if not text:
            return {"text": fallback, "generator": "reasoning-engine (empty model response)"}
        return {"text": text, "generator": f"reasoning-engine + {settings.llm_model}"}
    except Exception as exc:  # pragma: no cover
        log.warning("LLM call failed: %s", exc)
        return {"text": fallback, "generator": f"reasoning-engine (model unavailable: {type(exc).__name__})"}


def clarify_message(
    ctx: Dict[str, Any], questions: List[Dict[str, Any]], known_summary: str
) -> Dict[str, str]:
    """Short, non-repetitive acknowledgement + the questions that remain."""
    known = known_summary or "no site variables yet"
    body = (
        f"Recorded so far: {known}. "
        "Two things would change the recommendation materially, so I'll ask for them before analysing."
        if len(questions) > 1
        else f"Recorded so far: {known}. One more variable would change the ranking, so I'll ask for it first."
    )
    if not settings.llm_enabled:
        return {"text": body, "generator": "reasoning-engine (no API key set)"}

    client = _client()
    if client is None:
        return {"text": body, "generator": "reasoning-engine (SDK unavailable)"}

    prompt = (
        "You are an AI environmental scientist gathering site data. Acknowledge what is already known in one "
        "sentence, then in one or two more sentences explain why the listed questions would change the "
        "recommendation. 50-80 words, plain prose, no bullets, no greeting, do not repeat the questions verbatim "
        "and do not ask anything not listed.\n\n"
        f"KNOWN: {_format_context(ctx)}\n\n"
        "QUESTIONS PENDING:\n"
        + "\n".join(f"- {q['question']} (matters because: {q['why_it_matters']})" for q in questions)
    )
    try:
        response = client.messages.create(
            model=settings.llm_model,
            max_tokens=500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in response.content if getattr(b, "type", "") == "text").strip()
        return {"text": text or body, "generator": f"reasoning-engine + {settings.llm_model}"}
    except Exception as exc:  # pragma: no cover
        log.warning("LLM clarify call failed: %s", exc)
        return {"text": body, "generator": "reasoning-engine (model unavailable)"}


def _fallback_narrative(
    ctx: Dict[str, Any],
    diagnosis: Dict[str, Any],
    recommendations: List[Dict[str, Any]],
    citations: List[Dict[str, Any]],
    assumptions: List[str],
) -> str:
    couplings = diagnosis["couplings"][:2]
    chain = " ".join(c["explanation"] for c in couplings)
    first = recommendations[0]["title"].lower() if recommendations else "the sequenced plan"
    second = recommendations[1]["title"].lower() if len(recommendations) > 1 else ""
    cites = ", ".join(f"[{c['id']}]" for c in citations[:4])
    assumed = (
        f" {assumptions[0]}" if assumptions else ""
    )
    sequence = (
        f"The sequence starts with {first}, because it relieves the constraint that otherwise caps every later "
        f"measure" + (f", and only then {second}, which needs that base in place to deliver." if second else ".")
    )
    return (
        f"{chain} {sequence} Expected changes, horizons and confidence for each step are set out in the cards "
        f"below, with the supporting evidence attached to each one: {cites}.{assumed}"
    )
