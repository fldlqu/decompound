"""Stable human and machine-readable representations of compounds."""

from __future__ import annotations

import json
from typing import Any

from .model import Compound
from .morphology import boundaries
from .rebuild import rebuild
from .validation import validate

SCHEMA_NAME = "decompound.analysis"
SCHEMA_VERSION = 1


def analysis_data(compound: Compound) -> dict[str, Any]:
    """Return the versioned, JSON-serializable analysis document."""
    report = validate(compound)
    rebuilt = rebuild(compound)

    current_gloss = compound.head.gloss or compound.head.lemma
    relations = []
    for index, step in enumerate(compound.steps, start=1):
        modifier_gloss = step.modifier.gloss or step.modifier.lemma
        current_gloss = step.rule.interpret(
            head=current_gloss, modifier=modifier_gloss
        )
        relations.append(
            {
                "index": index,
                "modifier": step.modifier.lemma,
                "stem": step.modifier.stem,
                "linking_form": step.effective_linking_form,
                "surface": step.modifier_form,
                "relation": step.rule.relation.value,
                "modifier_type": step.rule.modifier_type.value,
                "head_type": step.rule.head_type.value,
                "result_type": step.rule.result_type.value,
            }
        )

    components = [
        {
            "position": position,
            "lemma": lexeme.lemma,
            "stem": realized.stem,
            "linking_form": realized.linking_form,
            "surface": realized.surface,
            "semantic_type": lexeme.semantic_type.value,
            "is_head": realized.is_head,
            "sense_id": lexeme.sense_id,
            "source": lexeme.source,
        }
        for position, (lexeme, realized) in enumerate(
            zip(rebuilt.components, rebuilt.realization.components), start=1
        )
    ]

    return {
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "word": rebuilt.word,
        "components": report.components,
        "component_sequence": components,
        "boundaries": boundaries(compound),
        "semantic_type": compound.semantic_type.value,
        "head": {
            "lemma": compound.head.lemma,
            "stem": compound.head.stem,
            "semantic_type": compound.head.semantic_type.value,
            "sense_id": compound.head.sense_id,
            "source": compound.head.source,
        },
        "gloss": current_gloss,
        "generation": {
            "strategy": compound.metadata.strategy,
            "fallback_used": compound.metadata.fallback_used,
            "fallback_reason": compound.metadata.fallback_reason,
        },
        "validation": {
            "valid": report.valid,
            "count_valid": report.count_valid,
            "semantic_edges": len(report.edges),
            "characters": report.characters,
            "layers": [
                {
                    "name": layer.layer.value,
                    "valid": layer.valid,
                    "checks": list(layer.checks),
                }
                for layer in report.layers
            ],
        },
        "relations_inner_to_outer": relations,
    }


def analysis_json(compound: Compound) -> str:
    """Serialize one analysis document deterministically as Unicode JSON."""
    return json.dumps(
        analysis_data(compound),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def explanation_lines(compound: Compound) -> tuple[str, ...]:
    """Return a stable human-readable summary distinct from the JSON schema."""
    data = analysis_data(compound)
    lines = [
        str(data["word"]),
        f"components: {data['components']}",
        f"boundaries: {data['boundaries']}",
        f"type: {data['semantic_type']}",
        f"head: {data['head']['lemma']} ({data['head']['semantic_type']})",
        f"gloss: {data['gloss']}",
        f"strategy: {data['generation']['strategy']}",
    ]
    if data["generation"]["fallback_used"]:
        lines.append(f"fallback: {data['generation']['fallback_reason']}")
    return tuple(lines)
