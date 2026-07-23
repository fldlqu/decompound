import pytest

from decompound.model import Compound, Lexeme, Relation, Rule, SemanticType as T, Step


def lexeme(name, kind):
    return Lexeme(name, name, kind)


def test_flat_encoding_matches_right_branching_surface_order():
    head = lexeme("Stelle", T.INSTITUTION)
    inner = lexeme("Arbeit", T.ACTIVITY)
    outer = lexeme("Amt", T.INSTITUTION)
    inner_rule = Rule(
        T.ACTIVITY, T.INSTITUTION, T.INSTITUTION, Relation.MANAGES, ""
    )
    outer_rule = Rule(
        T.INSTITUTION, T.INSTITUTION, T.INSTITUTION, Relation.CONCERNS, ""
    )

    compound = Compound(head).extend(Step(inner, inner_rule))
    compound = compound.extend(Step(outer, outer_rule))

    assert compound.component_count == 3
    assert compound.semantic_type == T.INSTITUTION
    assert compound.components() == (outer, inner, head)


def test_extend_rejects_rule_whose_head_type_does_not_match_current_result():
    head = lexeme("System", T.SYSTEM)
    modifier = lexeme("Arbeit", T.ACTIVITY)
    wrong = Rule(T.ACTIVITY, T.DOCUMENT, T.DOCUMENT, Relation.REGULATES, "")

    with pytest.raises(ValueError, match="expects head type"):
        Compound(head).extend(Step(modifier, wrong))


def test_extend_rejects_modifier_type_mismatch():
    head = lexeme("System", T.SYSTEM)
    modifier = lexeme("Amt", T.INSTITUTION)
    rule = Rule(T.ACTIVITY, T.SYSTEM, T.SYSTEM, Relation.USED_FOR, "")

    with pytest.raises(ValueError, match="modifier semantic type"):
        Compound(head).extend(Step(modifier, rule))
