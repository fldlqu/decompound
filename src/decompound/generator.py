"""Constraint-driven finite and incrementally infinite generation."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .extension import audit_extension_options, choose_extension_step
from .left_extension import LeftExtensionResult, extend_left
from .lexicon import HEADS
from .model import Compound, GenerationMetadata, Lexeme, SemanticType, Step
from .planning import PlanningError, SemanticPlanner
from .safety import audit_safe_heads, safe_step


audit_safe_heads(HEADS)
audit_extension_options(tuple({head.semantic_type for head in HEADS}))


@dataclass(slots=True)
class Generator:
    rng: random.Random

    @classmethod
    def seeded(cls, seed: int | str | bytes | None = None) -> "Generator":
        return cls(random.Random(seed))

    def available_head_types(self) -> tuple[SemanticType, ...]:
        """Return selectable result types in stable enum order."""
        present = {head.semantic_type for head in HEADS}
        return tuple(kind for kind in SemanticType if kind in present)

    def choose_target_type(
        self, target_type: SemanticType | str | None = None,
    ) -> SemanticType:
        """Resolve an optional requested target type or choose one uniformly."""
        available = self.available_head_types()
        if not available:
            raise RuntimeError("no selectable compound head types")
        if target_type is None:
            return self.rng.choice(available)
        if isinstance(target_type, str):
            try:
                target_type = SemanticType(target_type.lower())
            except ValueError as exc:
                raise ValueError(f"unknown semantic target type: {target_type}") from exc
        if target_type not in available:
            raise ValueError(
                f"semantic target type {target_type.value} has no selectable head"
            )
        return target_type

    def choose_head(
        self, target_type: SemanticType | str | None = None,
    ) -> Lexeme:
        """Choose a head licensed for the resolved target semantic type."""
        kind = self.choose_target_type(target_type)
        candidates = tuple(
            head for head in HEADS
            if head.semantic_type == kind and head.allowed_as_head
        )
        if not candidates:
            raise RuntimeError(f"no head candidates for semantic type {kind.value}")
        return self.rng.choice(candidates)

    def start(
        self, target_type: SemanticType | str | None = None,
    ) -> Compound:
        return Compound(self.choose_head(target_type))

    def _step_for_type(self, head_type: SemanticType) -> Step:
        """Choose from enumerated realizable edges with safe total fallback."""
        return choose_extension_step(head_type, self.rng)

    def next_step(self, compound: Compound) -> Step:
        step = self._step_for_type(compound.semantic_type)
        if not step.rule.accepts(
            step.modifier.semantic_type, compound.semantic_type
        ):
            raise RuntimeError("extension selector returned an illegal relation edge")
        return step

    def extend_left(self, compound: Compound) -> LeftExtensionResult:
        """Select and verify one new outermost/leftmost lexical component."""
        return extend_left(compound, self.next_step(compound))

    def extend(self, compound: Compound) -> Compound:
        """Compatibility convenience returning only the verified new state."""
        return self.extend_left(compound).compound

    def generate(
        self,
        length: int,
        target_type: SemanticType | str | None = None,
    ) -> Compound:
        if isinstance(length, bool) or not isinstance(length, int) or length < 1:
            raise ValueError("length must be an integer >= 1")
        # Resolve the target first, then construct exactly N semantic nodes with
        # a DP feasibility proof. Safe fallback is handled separately when rich
        # planning cannot produce a path.
        resolved_target = self.choose_target_type(target_type)
        head = self.choose_head(resolved_target)
        planner = SemanticPlanner(self.rng)
        try:
            plan = planner.plan(head, length, resolved_target)
        except PlanningError:
            steps = []
            current_type = head.semantic_type
            for _ in range(length - 1):
                step = safe_step(current_type, self.rng)
                steps.append(step)
                current_type = step.rule.result_type
            return Compound(
                head,
                tuple(steps),
                GenerationMetadata(
                    strategy="safe-skeleton",
                    fallback_used=True,
                    fallback_reason="rich semantic planner found no exact path",
                ),
            )
        return Compound(
            plan.head,
            plan.steps,
            GenerationMetadata(strategy="constrained-dp"),
        )
