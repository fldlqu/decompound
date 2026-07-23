"""Contracts shared by optional external lexical resources."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Protocol

from ..model import Gender, Lexeme, Register, SemanticType


class Confidence(StrEnum):
    UNVERIFIED = "unverified"
    MAPPED = "mapped"
    CURATED = "curated"


@dataclass(frozen=True, slots=True)
class ExternalCandidate:
    """Resource evidence that is not yet licensed for strict generation."""

    lemma: str
    semantic_type: SemanticType | None
    source: str
    sense_id: str | None = None
    gloss: str = ""
    confidence: Confidence = Confidence.UNVERIFIED


@dataclass(frozen=True, slots=True)
class NormalizationSpec:
    """Human- or project-approved morphology required for strict admission."""

    stem: str
    linking_forms: tuple[str, ...]
    preferred_linking_form: str
    gender: Gender = Gender.NEUTER
    allowed_as_modifier: bool = True
    allowed_as_head: bool = False
    register: Register = Register.NEUTRAL


class LexicalAdapter(Protocol):
    name: str

    def candidates(self, lemma: str) -> Iterable[ExternalCandidate]: ...


def normalize_candidate(
    candidate: ExternalCandidate,
    spec: NormalizationSpec,
    *,
    semantic_type: SemanticType | None = None,
) -> Lexeme:
    """Admit external evidence only after explicit morphology/type approval."""
    kind = semantic_type or candidate.semantic_type
    if kind is None:
        raise ValueError("external candidate needs an approved semantic type")
    if candidate.confidence is Confidence.UNVERIFIED:
        raise ValueError("unverified external candidate cannot enter strict generation")
    return Lexeme(
        lemma=candidate.lemma,
        stem=spec.stem,
        semantic_type=kind,
        linking_forms=spec.linking_forms,
        preferred_linking_form=spec.preferred_linking_form,
        gender=spec.gender,
        gloss=candidate.gloss,
        allowed_as_modifier=spec.allowed_as_modifier,
        allowed_as_head=spec.allowed_as_head,
        register=spec.register,
        source=candidate.source,
        sense_id=candidate.sense_id,
    )
