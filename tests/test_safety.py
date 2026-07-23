import random

import pytest

from decompound.lexicon import HEADS
from decompound.model import Lexeme, SemanticType as T
from decompound.safety import SAFE_SKELETONS, SafeSkeleton, audit_safe_heads, safe_step


def test_every_selectable_head_type_has_a_safe_skeleton():
    audit_safe_heads(HEADS)
    assert {head.semantic_type for head in HEADS} <= set(SAFE_SKELETONS)


def test_safe_steps_are_closed_and_repeatable():
    rng = random.Random(9)
    for kind, skeleton in SAFE_SKELETONS.items():
        current = kind
        for _ in range(1000):
            step = skeleton.step(rng)
            assert step.modifier.semantic_type == kind
            assert step.rule.head_type == current == kind
            assert step.rule.result_type == kind
            current = step.rule.result_type


def test_safe_step_is_total_for_every_selectable_head_type():
    rng = random.Random(3)
    for head in HEADS:
        step = safe_step(head.semantic_type, rng)
        assert step.rule.head_type == head.semantic_type
        assert step.rule.result_type == head.semantic_type


def test_head_audit_rejects_uncovered_type():
    uncovered = Lexeme("Ort", "Ort", T.LOCATION)
    with pytest.raises(RuntimeError, match="without safe recursive skeleton"):
        audit_safe_heads((uncovered,))


def test_skeleton_rejects_empty_modifier_pool():
    template = SAFE_SKELETONS[T.SYSTEM]
    with pytest.raises(ValueError, match="at least one modifier"):
        SafeSkeleton(T.SYSTEM, template.rule, ())
