"""Typed semantic grammar.

The first rule is the closure witness: an institution concerning another
institution remains an institution. Consequently it can be applied any finite
number of times, proving that generation need never run out of legal steps.
"""

from __future__ import annotations

from .model import Relation as R, Rule, SemanticType as T

RULES: tuple[Rule, ...] = (
    Rule(T.INSTITUTION, T.INSTITUTION, T.INSTITUTION, R.CONCERNS,
         "the {head} concerning the {modifier}", recursive=True),
    Rule(T.SUBJECT, T.INSTITUTION, T.INSTITUTION, R.CONCERNS,
         "the {head} responsible for {modifier}"),
    Rule(T.ACTIVITY, T.INSTITUTION, T.INSTITUTION, R.MANAGES,
         "the {head} managing {modifier}"),
    Rule(T.PROCESS, T.INSTITUTION, T.INSTITUTION, R.MANAGES,
         "the {head} managing {modifier}"),
    Rule(T.SUBJECT, T.SYSTEM, T.SYSTEM, R.PROCESSES,
         "the {head} processing {modifier}"),
    Rule(T.MATERIAL, T.SYSTEM, T.SYSTEM, R.PROCESSES,
         "the {head} processing {modifier}"),
    Rule(T.ACTIVITY, T.SYSTEM, T.SYSTEM, R.USED_FOR,
         "the {head} used for {modifier}"),
    Rule(T.SYSTEM, T.SYSTEM, T.SYSTEM, R.CONCERNS,
         "the {head} belonging to the {modifier}", recursive=True),
    Rule(T.SUBJECT, T.PROCESS, T.PROCESS, R.EXAMINES,
         "the {head} examining {modifier}"),
    Rule(T.ACTIVITY, T.PROCESS, T.PROCESS, R.EXAMINES,
         "the {head} examining {modifier}"),
    Rule(T.PROCESS, T.PROCESS, T.PROCESS, R.EXAMINES,
         "the {head} examining {modifier}", recursive=True),
    Rule(T.SUBJECT, T.DOCUMENT, T.DOCUMENT, R.REGULATES,
         "the {head} regulating {modifier}"),
    Rule(T.ACTIVITY, T.DOCUMENT, T.DOCUMENT, R.REGULATES,
         "the {head} regulating {modifier}"),
    Rule(T.DOCUMENT, T.DOCUMENT, T.DOCUMENT, R.CONCERNS,
         "the {head} concerning the {modifier}", recursive=True),
)

BY_HEAD: dict[T, tuple[Rule, ...]] = {
    t: tuple(rule for rule in RULES if rule.head_type == t) for t in T
}

BY_SIGNATURE: dict[tuple[T, T], tuple[Rule, ...]] = {
    (modifier, head): tuple(
        rule for rule in RULES
        if rule.modifier_type == modifier and rule.head_type == head
    )
    for modifier in T
    for head in T
}

CLOSURE_RULE: dict[T, Rule] = {
    rule.head_type: rule for rule in RULES if rule.recursive
}


def applicable_rules(modifier_type: T, head_type: T) -> tuple[Rule, ...]:
    """Return all semantic relations licensed for the two input types."""
    return BY_SIGNATURE[(modifier_type, head_type)]


def audit_relations() -> None:
    """Check uniqueness and closure assumptions of the core relation grammar."""
    identities = [
        (rule.modifier_type, rule.head_type, rule.result_type, rule.relation)
        for rule in RULES
    ]
    if len(identities) != len(set(identities)):
        raise RuntimeError("duplicate typed semantic relation")
    recursive_types = [rule.head_type for rule in RULES if rule.recursive]
    if len(recursive_types) != len(set(recursive_types)):
        raise RuntimeError("more than one closure rule for a semantic type")
    for kind, rule in CLOSURE_RULE.items():
        if rule.signature != (kind, kind, kind):
            raise RuntimeError(f"invalid closure signature for {kind}")


audit_relations()
