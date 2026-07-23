import pytest

from decompound import (
    Generator,
    SemanticType as T,
    ValidationError,
    ValidationLayer,
    validate,
    validate_morphology,
    validate_orthography,
    validate_semantics,
    validate_structure,
)
from decompound.model import Compound, Lexeme, Relation, Rule, Step


def test_success_report_has_all_layers_in_order():
    compound = Generator.seeded("layers").generate(30, T.SYSTEM)
    report = validate(compound, 30)
    assert [item.layer for item in report.layers] == [
        ValidationLayer.STRUCTURE,
        ValidationLayer.SEMANTICS,
        ValidationLayer.MORPHOLOGY,
        ValidationLayer.ORTHOGRAPHY,
    ]
    assert all(item.valid and item.checks for item in report.layers)
    assert report.layer(ValidationLayer.SEMANTICS).valid


def test_public_layer_functions_compose():
    compound = Generator.seeded(4).generate(20, T.DOCUMENT)
    structure = validate_structure(compound, 20)
    semantics, edges = validate_semantics(compound)
    morphology, realization = validate_morphology(compound)
    orthography = validate_orthography(realization.word)
    assert structure.layer == ValidationLayer.STRUCTURE
    assert semantics.layer == ValidationLayer.SEMANTICS
    assert len(edges) == 19
    assert morphology.layer == ValidationLayer.MORPHOLOGY
    assert orthography.layer == ValidationLayer.ORTHOGRAPHY


def test_semantic_failure_occurs_before_morphology():
    head = Lexeme("System", "System", T.SYSTEM)
    modifier = Lexeme("Arbeit", "Arbeit", T.ACTIVITY)
    wrong = Rule(
        T.ACTIVITY, T.DOCUMENT, T.DOCUMENT, Relation.REGULATES,
        "the {head} regulating {modifier}",
    )
    compound = Compound(head, (Step(modifier, wrong),))
    with pytest.raises(ValidationError, match="edge 1: rule expects"):
        validate(compound)


def test_morphology_failure_has_layer_prefix_for_bypassed_state():
    head = Lexeme("System", "System", T.SYSTEM)
    modifier = Lexeme("Netz", "Netz", T.SYSTEM, allowed_as_modifier=False)
    rule = Rule(
        T.SYSTEM, T.SYSTEM, T.SYSTEM, Relation.CONCERNS,
        "the {head} concerning {modifier}", recursive=True,
    )
    step = object.__new__(Step)
    object.__setattr__(step, "modifier", modifier)
    object.__setattr__(step, "rule", rule)
    object.__setattr__(step, "linking_form", "")
    with pytest.raises(ValidationError, match="morphology: edge 1"):
        validate(Compound(head, (step,)))


@pytest.mark.parametrize(
    "word", ["", "system", "System Plan", "System-Plan", "System2", "Gro\u0308ße"]
)
def test_orthography_layer_rejects_invalid_strict_outputs(word):
    with pytest.raises(ValidationError, match="orthography:"):
        validate_orthography(word)
