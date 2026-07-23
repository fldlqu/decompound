"""Constrained randomized planning for exact-size semantic structures."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .lexicon import BY_TYPE
from .model import Lexeme, Rule, SemanticType, Step
from .relations import BY_HEAD


class PlanningError(RuntimeError):
    """Raised when no typed path can satisfy a requested plan."""


@dataclass(frozen=True, slots=True)
class Transition:
    """A rule paired with the non-empty modifier pool that realizes it."""

    rule: Rule
    modifiers: tuple[Lexeme, ...]

    def __post_init__(self) -> None:
        if not self.modifiers:
            raise ValueError("transition requires a non-empty modifier pool")
        if any(
            modifier.semantic_type != self.rule.modifier_type
            or not modifier.allowed_as_modifier
            for modifier in self.modifiers
        ):
            raise ValueError("transition modifier pool violates its rule signature")

    @property
    def input_type(self) -> SemanticType:
        return self.rule.head_type

    @property
    def output_type(self) -> SemanticType:
        return self.rule.result_type

    def choose_step(self, rng: random.Random) -> Step:
        return Step(rng.choice(self.modifiers), self.rule)


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    """A head plus exactly the planned inner-to-outer composition steps."""

    head: Lexeme
    steps: tuple[Step, ...]
    target_type: SemanticType

    @property
    def component_count(self) -> int:
        return 1 + len(self.steps)

    @property
    def result_type(self) -> SemanticType:
        return self.steps[-1].rule.result_type if self.steps else self.head.semantic_type


class SemanticPlanner:
    """Dynamic-programming planner over typed composition transitions.

    The planner first proves which semantic types can reach the requested final
    type in exactly k extension steps. Random choices are then restricted to
    transitions that preserve that exact remaining-step feasibility.
    """

    def __init__(self, rng: random.Random):
        self.rng = rng
        self._transitions = self._build_transitions()

    @staticmethod
    def _build_transitions() -> dict[SemanticType, tuple[Transition, ...]]:
        result: dict[SemanticType, tuple[Transition, ...]] = {}
        for head_type in SemanticType:
            transitions = []
            for rule in BY_HEAD.get(head_type, ()):
                pool = tuple(
                    modifier for modifier in BY_TYPE.get(rule.modifier_type, ())
                    if modifier.allowed_as_modifier
                )
                if pool:
                    transitions.append(Transition(rule, pool))
            result[head_type] = tuple(transitions)
        return result

    def feasible_types(
        self,
        steps: int,
        target_type: SemanticType,
    ) -> tuple[frozenset[SemanticType], ...]:
        """Return DP layers where layer k reaches target in exactly k steps."""
        if steps < 0:
            raise ValueError("steps must be >= 0")
        layers: list[frozenset[SemanticType]] = [frozenset({target_type})]
        for _ in range(steps):
            previous = layers[-1]
            current = {
                head_type
                for head_type, transitions in self._transitions.items()
                if any(t.output_type in previous for t in transitions)
            }
            layers.append(frozenset(current))
        return tuple(layers)

    def plan(
        self,
        head: Lexeme,
        component_count: int,
        target_type: SemanticType,
    ) -> GenerationPlan:
        if isinstance(component_count, bool) or not isinstance(component_count, int):
            raise ValueError("component_count must be an integer >= 1")
        if component_count < 1:
            raise ValueError("component_count must be an integer >= 1")
        if not head.allowed_as_head:
            raise PlanningError(f"{head.lemma} is not licensed as a head")

        remaining = component_count - 1
        layers = self.feasible_types(remaining, target_type)
        current_type = head.semantic_type
        if current_type not in layers[remaining]:
            raise PlanningError(
                f"head type {current_type.value} cannot reach {target_type.value} "
                f"in exactly {remaining} steps"
            )

        steps: list[Step] = []
        while remaining:
            next_feasible = layers[remaining - 1]
            candidates = tuple(
                transition
                for transition in self._transitions.get(current_type, ())
                if transition.output_type in next_feasible
            )
            if not candidates:
                raise PlanningError(
                    f"no transition from {current_type.value} with "
                    f"{remaining} steps remaining"
                )
            transition = self.rng.choice(candidates)
            step = transition.choose_step(self.rng)
            steps.append(step)
            current_type = transition.output_type
            remaining -= 1

        if current_type != target_type:
            raise PlanningError(
                f"planner ended at {current_type.value}, expected {target_type.value}"
            )
        return GenerationPlan(head, tuple(steps), target_type)
