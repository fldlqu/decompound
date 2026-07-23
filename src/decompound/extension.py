"""Selection and auditing of legal one-step compound extensions."""

from __future__ import annotations

import random
from dataclasses import dataclass

from .lexicon import BY_TYPE
from .model import Lexeme, Rule, SemanticType, Step
from .relations import BY_HEAD
from .safety import safe_step


@dataclass(frozen=True, slots=True)
class ExtensionOption:
    """A relation plus its complete non-empty licensed modifier pool."""

    rule: Rule
    modifiers: tuple[Lexeme, ...]

    def __post_init__(self) -> None:
        if not self.modifiers:
            raise ValueError("extension option requires modifiers")
        if any(not modifier.allowed_as_modifier for modifier in self.modifiers):
            raise ValueError("extension option contains a modifier-forbidden lexeme")
        if any(
            modifier.semantic_type != self.rule.modifier_type
            for modifier in self.modifiers
        ):
            raise ValueError("extension option modifier type violates rule signature")

    @property
    def head_type(self) -> SemanticType:
        return self.rule.head_type

    @property
    def result_type(self) -> SemanticType:
        return self.rule.result_type

    def choose(self, rng: random.Random) -> Step:
        return Step(rng.choice(self.modifiers), self.rule)


def legal_extension_options(head_type: SemanticType) -> tuple[ExtensionOption, ...]:
    """Enumerate all currently realizable relation choices for a head type."""
    options: list[ExtensionOption] = []
    for rule in BY_HEAD.get(head_type, ()):
        modifiers = tuple(
            modifier
            for modifier in BY_TYPE.get(rule.modifier_type, ())
            if modifier.allowed_as_modifier
            and modifier.semantic_type == rule.modifier_type
        )
        if modifiers:
            options.append(ExtensionOption(rule, modifiers))
    return tuple(options)


def choose_extension_step(head_type: SemanticType, rng: random.Random) -> Step:
    """Choose only from legal options, or use the proved total safe witness."""
    options = legal_extension_options(head_type)
    if not options:
        return safe_step(head_type, rng)
    option = rng.choice(options)
    return option.choose(rng)


def audit_extension_options(head_types: tuple[SemanticType, ...]) -> None:
    """Check every exposed option and totality for selectable current types."""
    for head_type in head_types:
        options = legal_extension_options(head_type)
        if not options:
            # This must itself be total for selectable types.
            safe_step(head_type, random.Random(0))
            continue
        for option in options:
            if option.head_type != head_type:
                raise RuntimeError("extension index returned wrong head type")
            for modifier in option.modifiers:
                if not option.rule.accepts(modifier.semantic_type, head_type):
                    raise RuntimeError("extension option violates relation signature")
