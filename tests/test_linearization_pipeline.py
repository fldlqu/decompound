import unicodedata

import pytest

from decompound import Generator, linearization_result, validate
from decompound.model import Compound, Lexeme, Relation, Rule, SemanticType as T, Step
from decompound.morphology import MorphologyError


def preserving_rule(modifier_type, head_type):
    return Rule(
        modifier_type, head_type, head_type, Relation.CONCERNS,
        "the {head} concerning {modifier}",
    )


@pytest.mark.parametrize("length", [1, 2, 17, 500])
def test_generated_pipeline_is_component_preserving_and_nfc(length):
    compound = Generator.seeded(length).generate(length)
    result = linearization_result(compound)
    assert len(result.components) == length
    assert len(result.linking_forms) == length - 1
    assert result.word.isalpha()
    assert result.word[0].isupper()
    assert unicodedata.is_normalized("NFC", result.word)
    assert "".join(
        component.surface[:1].lower() + component.surface[1:]
        for component in result.components
    ).capitalize() == result.word
    validate(compound, length)


def test_explicit_empty_link_is_applied_without_adding_material():
    head = Lexeme("Amt", "Amt", T.INSTITUTION)
    modifier = Lexeme(
        "Arbeit", "Arbeit", T.ACTIVITY,
        linking_forms=("", "s"), preferred_linking_form="s",
    )
    step = Step(
        modifier,
        preserving_rule(T.ACTIVITY, T.INSTITUTION),
        linking_form="",
    )
    result = linearization_result(Compound(head, (step,)))
    assert result.components[0].linking_form == ""
    assert result.components[0].surface == "Arbeit"
    assert result.word == "Arbeitamt"


def test_pipeline_rechecks_modifier_role_even_for_bypassed_step():
    head = Lexeme("Amt", "Amt", T.INSTITUTION)
    modifier = Lexeme(
        "System", "System", T.SYSTEM,
        allowed_as_modifier=False,
        allowed_as_head=True,
    )
    step = object.__new__(Step)
    object.__setattr__(step, "modifier", modifier)
    object.__setattr__(
        step, "rule", preserving_rule(T.SYSTEM, T.INSTITUTION),
    )
    object.__setattr__(step, "linking_form", "")
    with pytest.raises(MorphologyError, match="not licensed as a modifier"):
        linearization_result(Compound(head, (step,)))
