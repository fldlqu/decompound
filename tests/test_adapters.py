import pytest

from decompound.adapters import (
    Confidence,
    ExternalCandidate,
    NormalizationSpec,
    normalize_candidate,
)
from decompound.adapters.splitter import SplitDiagnostic, diagnose
from decompound.model import SemanticType as T



def test_unverified_candidate_cannot_enter_strict_generation():
    candidate = ExternalCandidate("Werk", T.ARTIFACT, "fixture")
    spec = NormalizationSpec("Werk", ("s",), "s")
    with pytest.raises(ValueError, match="unverified"):
        normalize_candidate(candidate, spec)


def test_mapped_candidate_requires_explicit_morphology_and_normalizes():
    candidate = ExternalCandidate(
        "Werk", T.ARTIFACT, "fixture", "fixture:1", "work",
        Confidence.MAPPED,
    )
    spec = NormalizationSpec("Werk", ("", "s"), "s")
    lexeme = normalize_candidate(candidate, spec)
    assert lexeme.semantic_type == T.ARTIFACT
    assert lexeme.modifier_form == "Werks"
    assert lexeme.source == "fixture"



class MisleadingSplitter:
    name = "fixture"

    def split(self, word):
        return SplitDiagnostic(self.name, word, ("Test", "Wort"), 0.9, True)


def test_splitter_diagnostic_can_never_claim_authority():
    result = diagnose(MisleadingSplitter(), "Testwort")
    assert result.parts == ("Test", "Wort")
    assert not result.authoritative
