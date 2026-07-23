import pytest

from decompound import Generator, SemanticType as T, ValidationError, validate, validate_semantic_edges
from decompound.model import Compound, Lexeme, Relation, Rule, Step


def test_every_generated_edge_is_reported_inner_to_outer():
    compound = Generator.seeded("edges").generate(100, T.DOCUMENT)
    edges = validate_semantic_edges(compound)
    assert len(edges) == 99
    current = compound.head.semantic_type
    for index, (step, edge) in enumerate(zip(compound.steps, edges), start=1):
        assert edge.index == index
        assert edge.modifier == step.modifier.lemma
        assert edge.relation == step.rule.relation.value
        assert edge.input_head_type == current
        assert edge.modifier_type == step.modifier.semantic_type
        assert edge.result_type == step.rule.result_type
        assert edge.valid
        current = edge.result_type
    assert current == compound.semantic_type


def test_validation_report_contains_edge_fold_and_final_type():
    compound = Generator.seeded(3).generate(12, T.SYSTEM)
    report = validate(compound, 12)
    assert len(report.edges) == 11
    assert report.final_semantic_type == T.SYSTEM


def test_one_component_compound_has_no_relation_edges():
    compound = Generator.seeded(3).generate(1, T.PROCESS)
    report = validate(compound, 1)
    assert report.edges == ()
    assert report.final_semantic_type == T.PROCESS


def test_validator_localizes_wrong_head_input_type():
    head = Lexeme("System", "System", T.SYSTEM)
    modifier = Lexeme("Arbeit", "Arbeit", T.ACTIVITY)
    wrong_rule = Rule(
        T.ACTIVITY, T.DOCUMENT, T.DOCUMENT, Relation.REGULATES,
        "the {head} regulating {modifier}",
    )
    malformed = Compound(head, (Step(modifier, wrong_rule),))
    with pytest.raises(
        ValidationError,
        match="edge 1: rule expects head type document, got system",
    ):
        validate_semantic_edges(malformed)


def test_validator_localizes_wrong_modifier_type():
    head = Lexeme("System", "System", T.SYSTEM)
    modifier = Lexeme("Amt", "Amt", T.INSTITUTION)
    rule = Rule(
        T.ACTIVITY, T.SYSTEM, T.SYSTEM, Relation.USED_FOR,
        "the {head} used for {modifier}",
    )
    # Step itself accepts morphology; the independent semantic validator must
    # catch this directly constructed malformed relation edge.
    malformed = object.__new__(Step)
    object.__setattr__(malformed, "modifier", modifier)
    object.__setattr__(malformed, "rule", rule)
    object.__setattr__(malformed, "linking_form", None)
    compound = Compound(head, (malformed,))
    with pytest.raises(
        ValidationError,
        match="edge 1: modifier Amt has type institution, expected activity",
    ):
        validate_semantic_edges(compound)
