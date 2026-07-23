"""Verified one-component left extension of right-headed compounds."""

from __future__ import annotations

from dataclasses import dataclass

from .model import Compound, Step
from .morphology import realize_modifier
from .rebuild import RebuildResult, rebuild


class LeftExtensionError(RuntimeError):
    """Raised when an extension fails the structural left-extension contract."""


@dataclass(frozen=True, slots=True)
class LeftExtensionResult:
    """The old and new immutable states plus their observable word delta."""

    previous: Compound
    compound: Compound
    step: Step
    previous_word: str
    word: str
    added_surface: str
    rebuilt: RebuildResult

    @property
    def added_components(self) -> int:
        return self.compound.component_count - self.previous.component_count


def internalize(word: str) -> str:
    """Return the spelling of a formerly standalone noun inside a larger word."""
    return word[:1].lower() + word[1:]


def extend_left(compound: Compound, step: Step) -> LeftExtensionResult:
    """Apply and verify ``new = modifier + old`` without mutating old state."""
    previous_rebuild = rebuild(compound)
    previous_word = previous_rebuild.word
    previous_components = compound.components()
    previous_steps = compound.steps

    extended = compound.extend(step)
    rebuilt = rebuild(extended)
    word = rebuilt.word
    added_surface = realize_modifier(step)

    if extended.component_count != compound.component_count + 1:
        raise LeftExtensionError("left extension did not add exactly one component")
    if extended.head is not compound.head:
        raise LeftExtensionError("left extension replaced the rightmost head")
    if extended.steps[:-1] != previous_steps or extended.steps[-1] != step:
        raise LeftExtensionError("left extension did not preserve prior steps")
    if extended.components() != (step.modifier,) + previous_components:
        raise LeftExtensionError("new modifier is not the leftmost component")
    expected_word = added_surface[:1].upper() + added_surface[1:] + internalize(
        previous_word
    )
    if word != expected_word:
        raise LeftExtensionError(
            "linearized extension does not preserve the previous word as suffix"
        )

    return LeftExtensionResult(
        previous=compound,
        compound=extended,
        step=step,
        previous_word=previous_word,
        word=word,
        added_surface=added_surface,
        rebuilt=rebuilt,
    )
