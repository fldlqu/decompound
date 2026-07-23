"""Optional external NLP integrations.

Adapters return evidence-only candidates. Strict generation accepts them only
after explicit normalization to the core `Lexeme` contract.
"""

from .base import (
    Confidence,
    ExternalCandidate,
    LexicalAdapter,
    NormalizationSpec,
    normalize_candidate,
)

__all__ = [
    "Confidence",
    "ExternalCandidate",
    "LexicalAdapter",
    "NormalizationSpec",
    "normalize_candidate",
]
