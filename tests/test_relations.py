import pytest

from decompound.model import Relation, Rule, SemanticType as T
from decompound.relations import CLOSURE_RULE, RULES, applicable_rules, audit_relations


def test_every_rule_has_a_queryable_exact_signature():
    for rule in RULES:
        assert rule in applicable_rules(rule.modifier_type, rule.head_type)
        assert rule.accepts(rule.modifier_type, rule.head_type)


def test_wrong_input_type_is_not_accepted():
    rule = RULES[0]
    assert not rule.accepts(T.MATERIAL, rule.head_type)
    assert not rule.accepts(rule.modifier_type, T.LOCATION)


def test_recursive_rules_are_closed():
    for kind, rule in CLOSURE_RULE.items():
        assert rule.recursive
        assert rule.signature == (kind, kind, kind)


def test_non_closed_recursive_rule_is_rejected():
    with pytest.raises(ValueError, match="must be closed"):
        Rule(
            T.SUBJECT,
            T.DOCUMENT,
            T.DOCUMENT,
            Relation.REGULATES,
            "the {head} for {modifier}",
            recursive=True,
        )


@pytest.mark.parametrize("template", ["only {head}", "only {modifier}", "neither"])
def test_gloss_template_must_name_both_arguments(template):
    with pytest.raises(ValueError, match="gloss template"):
        Rule(T.SUBJECT, T.DOCUMENT, T.DOCUMENT, Relation.CONCERNS, template)


def test_interpretation_uses_both_semantic_arguments():
    rule = applicable_rules(T.ACTIVITY, T.SYSTEM)[0]
    gloss = rule.interpret(modifier="research", head="system")
    assert "research" in gloss
    assert "system" in gloss


def test_core_relation_audit_passes():
    audit_relations()
