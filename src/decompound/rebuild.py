"""Canonical rebuilding of complete compounds after incremental extension."""

from __future__ import annotations

from dataclasses import dataclass

from .model import Compound, Lexeme, Step
from .morphology import LinearizationResult, linearization_result


class RebuildError(RuntimeError):
    """Raised when canonical rebuilding disagrees with the model state."""


@dataclass(frozen=True, slots=True)
class RebuildResult:
    """A complete reconstruction derived only from canonical model fields."""

    compound: Compound
    components: tuple[Lexeme, ...]
    steps_inner_to_outer: tuple[Step, ...]
    realization: LinearizationResult

    @property
    def word(self) -> str:
        return self.realization.word

    @property
    def component_count(self) -> int:
        return len(self.components)


def rebuild(compound: Compound) -> RebuildResult:
    """Recompute the full component sequence and word from head plus all steps."""
    steps = tuple(compound.steps)
    components = tuple(step.modifier for step in reversed(steps)) + (
        compound.head,
    )
    realization = linearization_result(compound)

    if components != compound.components():
        raise RebuildError("rebuilt components disagree with compound traversal")
    if len(components) != compound.component_count:
        raise RebuildError("rebuilt component count disagrees with compound state")
    if len(realization.components) != len(components):
        raise RebuildError("realization omitted or added a rebuilt component")
    if tuple(item.lemma for item in realization.components) != tuple(
        item.lemma for item in components
    ):
        raise RebuildError("realization order disagrees with rebuilt components")

    return RebuildResult(compound, components, steps, realization)
