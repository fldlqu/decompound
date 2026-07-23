import random

import pytest

from decompound.lexicon import HEADS
from decompound.model import Lexeme, SemanticType as T
from decompound.planning import PlanningError, SemanticPlanner, Transition
from decompound.validation import validate
from decompound.model import Compound


def head(kind):
    return next(item for item in HEADS if item.semantic_type == kind)


@pytest.mark.parametrize("kind", [T.INSTITUTION, T.SYSTEM, T.PROCESS, T.DOCUMENT])
@pytest.mark.parametrize("length", [1, 2, 17, 250])
def test_planner_constructs_exact_typed_plan(kind, length):
    planner = SemanticPlanner(random.Random(4))
    plan = planner.plan(head(kind), length, kind)
    assert plan.component_count == length
    assert plan.result_type == kind
    validate(Compound(plan.head, plan.steps), length)


def test_feasibility_layers_have_exact_step_meaning_for_closed_type():
    planner = SemanticPlanner(random.Random(1))
    layers = planner.feasible_types(20, T.SYSTEM)
    assert len(layers) == 21
    assert layers[0] == frozenset({T.SYSTEM})
    assert all(T.SYSTEM in layer for layer in layers)


def test_planner_rejects_impossible_target_path():
    planner = SemanticPlanner(random.Random(1))
    with pytest.raises(PlanningError, match="cannot reach"):
        planner.plan(head(T.SYSTEM), 10, T.DOCUMENT)


def test_transition_rejects_empty_or_mistyped_pool():
    planner = SemanticPlanner(random.Random(1))
    system_transition = planner._transitions[T.SYSTEM][0]
    with pytest.raises(ValueError, match="non-empty"):
        Transition(system_transition.rule, ())
    wrong = Lexeme("Amt", "Amt", T.INSTITUTION)
    with pytest.raises(ValueError, match="violates"):
        Transition(system_transition.rule, (wrong,))


def test_planning_is_reproducible():
    left = SemanticPlanner(random.Random(99)).plan(head(T.DOCUMENT), 100, T.DOCUMENT)
    right = SemanticPlanner(random.Random(99)).plan(head(T.DOCUMENT), 100, T.DOCUMENT)
    assert left == right
