"""Constructive witnesses for generation at every finite component count.

A safe skeleton is stronger than an ordinary recursive rule: it records a
non-empty modifier pool and a type-preserving rule. Repeating that witness keeps
the generator in the same semantic type, so another step is always available.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .lexicon import LEXEMES
from .model import Lexeme, Rule, SemanticType, Step
from .relations import CLOSURE_RULE


@dataclass(frozen=True, slots=True)
class SafeSkeleton:
    """A constructive witness for ``T + T -> T`` closure."""

    semantic_type: SemanticType
    rule: Rule
    modifiers: tuple[Lexeme, ...]

    def __post_init__(self) -> None:
        if not self.modifiers:
            raise ValueError("safe skeleton requires at least one modifier")
        if not self.rule.recursive:
            raise ValueError("safe skeleton rule must be marked recursive")
        if self.rule.head_type != self.semantic_type:
            raise ValueError("safe skeleton rule consumes the wrong head type")
        if self.rule.result_type != self.semantic_type:
            raise ValueError("safe skeleton rule is not type-preserving")
        if self.rule.modifier_type != self.semantic_type:
            raise ValueError("safe skeleton modifier type is not closed")
        if any(x.semantic_type != self.semantic_type for x in self.modifiers):
            raise ValueError("safe skeleton contains a modifier of the wrong type")

    def step(self, rng: random.Random) -> Step:
        return Step(rng.choice(self.modifiers), self.rule)


def _named(kind: SemanticType, *lemmas: str) -> tuple[Lexeme, ...]:
    selected = tuple(
        lexeme for lexeme in LEXEMES
        if lexeme.semantic_type == kind and lexeme.lemma in lemmas
    )
    missing = set(lemmas) - {lexeme.lemma for lexeme in selected}
    if missing:
        raise RuntimeError(f"safe skeleton lexemes missing: {sorted(missing)}")
    return selected


SAFE_SKELETONS: dict[SemanticType, SafeSkeleton] = {
    SemanticType.INSTITUTION: SafeSkeleton(
        SemanticType.INSTITUTION,
        CLOSURE_RULE[SemanticType.INSTITUTION],
        _named(SemanticType.INSTITUTION, "Verwaltung", "Amt", "Stelle"),
    ),
    SemanticType.SYSTEM: SafeSkeleton(
        SemanticType.SYSTEM,
        CLOSURE_RULE[SemanticType.SYSTEM],
        _named(SemanticType.SYSTEM, "System", "Netz"),
    ),
    SemanticType.PROCESS: SafeSkeleton(
        SemanticType.PROCESS,
        CLOSURE_RULE[SemanticType.PROCESS],
        _named(SemanticType.PROCESS, "Prüfung", "Kontrolle", "Verarbeitung"),
    ),
    SemanticType.DOCUMENT: SafeSkeleton(
        SemanticType.DOCUMENT,
        CLOSURE_RULE[SemanticType.DOCUMENT],
        _named(SemanticType.DOCUMENT, "Plan", "Gesetz", "Bericht"),
    ),
}


def safe_step(kind: SemanticType, rng: random.Random) -> Step:
    """Return a total, type-preserving extension for a guaranteed head type."""
    try:
        skeleton = SAFE_SKELETONS[kind]
    except KeyError as exc:
        raise ValueError(f"no safe recursive skeleton for semantic type {kind}") from exc
    return skeleton.step(rng)


def audit_safe_heads(heads: tuple[Lexeme, ...]) -> None:
    """Fail fast if a selectable head lacks a constructive closure witness."""
    uncovered = {head.semantic_type for head in heads} - set(SAFE_SKELETONS)
    if uncovered:
        names = ", ".join(sorted(x.value for x in uncovered))
        raise RuntimeError(f"heads without safe recursive skeleton: {names}")
