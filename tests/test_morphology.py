import unicodedata

import pytest

from decompound.model import Compound, Lexeme, Relation, Rule, SemanticType as T, Step
from decompound.morphology import (
    MorphologyError, boundaries, linearization_result, linearize,
    realize_components, surface_forms,
)


def rule(modifier_type, head_type):
    return Rule(
        modifier_type, head_type, head_type, Relation.CONCERNS,
        "the {head} concerning {modifier}",
    )


def test_linking_element_is_recorded_but_not_a_component():
    head = Lexeme("Amt", "Amt", T.INSTITUTION)
    modifier = Lexeme(
        "Arbeit", "Arbeit", T.ACTIVITY,
        linking_forms=("s",), preferred_linking_form="s",
    )
    compound = Compound(head, (Step(modifier, rule(T.ACTIVITY, T.INSTITUTION)),))
    assert linearize(compound) == "Arbeitsamt"
    assert boundaries(compound) == "Arbeit[s]+Amt"
    assert compound.component_count == 2


def test_step_can_select_a_nonpreferred_but_licensed_allomorph():
    head = Lexeme("Amt", "Amt", T.INSTITUTION)
    modifier = Lexeme(
        "Name", "Name", T.SUBJECT,
        linking_forms=("ns", "n"), preferred_linking_form="ns",
    )
    step = Step(modifier, rule(T.SUBJECT, T.INSTITUTION), linking_form="n")
    compound = Compound(head, (step,))
    assert linearize(compound) == "Namenamt"
    assert boundaries(compound) == "Name[n]+Amt"


def test_unlicensed_linking_allomorph_is_rejected():
    modifier = Lexeme("Arbeit", "Arbeit", T.ACTIVITY)
    with pytest.raises(ValueError, match="not licensed"):
        Step(modifier, rule(T.ACTIVITY, T.INSTITUTION), linking_form="s")


def test_modern_spelling_does_not_delete_triple_consonants():
    head = Lexeme("Stoff", "Stoff", T.MATERIAL)
    modifier = Lexeme("Schiff", "Schiff", T.ARTIFACT)
    compound = Compound(head, (Step(modifier, rule(T.ARTIFACT, T.MATERIAL)),))
    assert linearize(compound) == "Schiffstoff"


def test_output_is_nfc_normalized():
    decomposed = "A\u0308hre"
    modifier = Lexeme("Ähre", decomposed, T.MATERIAL)
    head = Lexeme("Feld", "Feld", T.LOCATION)
    compound = Compound(head, (Step(modifier, rule(T.MATERIAL, T.LOCATION)),))
    word = linearize(compound)
    assert word == "Ährefeld"
    assert unicodedata.is_normalized("NFC", word)


def test_pipeline_exposes_surface_order_and_selected_links():
    head = Lexeme("Amt", "Amt", T.INSTITUTION)
    inner = Lexeme(
        "Arbeit", "Arbeit", T.ACTIVITY,
        linking_forms=("s",), preferred_linking_form="s",
    )
    outer = Lexeme(
        "Name", "Name", T.SUBJECT,
        linking_forms=("n", "ns"), preferred_linking_form="ns",
    )
    compound = Compound(head, (
        Step(inner, rule(T.ACTIVITY, T.INSTITUTION)),
        Step(outer, rule(T.SUBJECT, T.INSTITUTION), linking_form="n"),
    ))
    result = linearization_result(compound)
    assert result.word == "Namenarbeitsamt"
    assert result.linking_forms == ("n", "s")
    assert [component.lemma for component in result.components] == [
        "Name", "Arbeit", "Amt",
    ]
    assert [component.source_step_index for component in result.components] == [
        2, 1, None,
    ]
    assert surface_forms(compound) == ("Namen", "Arbeits", "Amt")
    assert boundaries(compound) == "Name[n]+Arbeit[s]+Amt"


def test_realization_has_one_record_per_semantic_component():
    head = Lexeme("Amt", "Amt", T.INSTITUTION)
    modifier = Lexeme(
        "Arbeit", "Arbeit", T.ACTIVITY,
        linking_forms=("", "s"), preferred_linking_form="s",
    )
    compound = Compound(head, (Step(modifier, rule(T.ACTIVITY, T.INSTITUTION)),))
    assert len(realize_components(compound)) == compound.component_count


def test_head_must_be_head_licensed():
    head = Lexeme("Amt", "Amt", T.INSTITUTION, allowed_as_head=False)
    with pytest.raises(MorphologyError, match="not licensed as a head"):
        surface_forms(Compound(head))
